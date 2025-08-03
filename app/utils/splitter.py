"""Утилита разбиения текста договора на читаемые чанки.

Алгоритм рекурсивного деления:

1. Заголовки ^\d+\.\s+.+
2. Пустые строки
3. Предложения (если включен split_sentences)
4. Fallback — токенное окно <= max_tokens

Особенности:
- OCR-нормализация мусора (переносы, soft-hyphen, футеры, тире)
- Overlap внутри раздела (overlap токенов)
- Dedup MinHash (20-словные шинглы, Jaccard > 0.9)
- LRU-кэш на 4000 строк для tiktoken.encode

Параметры берутся из settings.splitter или передаются в конструктор.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from functools import lru_cache
from itertools import pairwise

import structlog
import tiktoken
from datasketch import MinHash

from app.core.settings import settings

logger = structlog.get_logger(__name__)

_ENCODING = tiktoken.get_encoding("cl100k_base")


@lru_cache(maxsize=4_000)
def _encode(text: str) -> tuple[int, ...]:
    """Кэшированная обёртка над tiktoken.encode.

    Args:
        text (str): Входной текст.

    Returns:
        tuple[int, ...]: Токены текста.
    """
    return tuple(_ENCODING.encode(text))


class ContractSplitter:
    """Разбивает текст договора на читаемые чанки."""

    _HEADER_RE = re.compile(r"^\s*(\d+\.\s+[^\n]+)", re.M)
    _CLAUSE_RE = re.compile(r"^(\d+(?:\.\d+)+)")
    _EMPTY_RE = re.compile(r"\n\s*\n")
    _SENT_RE = re.compile(r"(?<=[.!?…])\s+(?=[А-ЯA-Z])")
    _SHINGLE_SIZE = 20
    _DEDUP_THRESHOLD = 0.9
    _MINHASH_NUM_PERM = 128

    def __init__(
        self,
        max_tokens: int | None = None,
        overlap: int | None = None,
        *,
        split_sentences: bool = True,
    ) -> None:
        """Инициализирует сплиттер с параметрами.

        Args:
            max_tokens (int | None): Максимум токенов на чанк.
            overlap (int | None): Количество overlap-токенов между чанками.
            split_sentences (bool): Делить по предложениям.
        """
        self.max_tokens = max_tokens or settings.splitter.max_tokens
        self.overlap = overlap or settings.splitter.overlap
        self.split_sentences = split_sentences
        if self.overlap >= self.max_tokens:
            raise ValueError("overlap должен быть меньше max_tokens")

    def split(self, text: str, meta: dict | None = None) -> list[dict]:
        """Разбивает text и добавляет meta к каждому чанку.

        Args:
            text (str): Исходный текст.
            meta (dict | None): Метаданные (например page_no).

        Returns:
            list[dict]: Список чанков с мета-информацией.
        """
        meta = meta or {}
        text_norm = self._normalize(text)
        raw_chunks: list[tuple[str | None, str]] = []

        for header, body in self._iter_sections(text_norm):
            for chunk in self._segment_section(body):
                raw_chunks.append((header, chunk))

        chunks = self._apply_overlap(raw_chunks)

        chunks_meta = [
            {
                "text": chunk.strip(),
                "page_no": meta.get("page_no"),
                "section_header": header,
                "clause_number": self._extract_clause(chunk),
                "chunk_idx": idx,
            }
            for idx, (header, chunk) in enumerate(chunks)
        ]

        return self._dedup(chunks_meta)

    @staticmethod
    def _normalize(text: str) -> str:
        """Удаляет мусор OCR/верстки и унифицирует символы.

        Args:
            text (str): Входной сырой текст.

        Returns:
            str: Нормализованный текст.
        """
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r"\u00AD", "", text)
        text = re.sub(r"([^\n])\n(?!\n)", r"\1 ", text)
        text = re.sub(r"\b(?:стр\.?|страница)\s*\d+\s*(?:из|/)\s*\d+\b", " ", text, flags=re.I)
        text = text.replace("–", "—").replace("-", "-")
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    def _iter_sections(self, text: str) -> Iterable[tuple[str | None, str]]:
        """Разделяет текст на разделы по заголовкам.

        Args:
            text (str): Полный нормализованный текст.

        Yields:
            tuple[str | None, str]: Заголовок и тело раздела.
        """
        matches = list(self._HEADER_RE.finditer(text))
        if not matches:
            yield None, text
            return
        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            yield m.group(1).strip(), text[start:end]

    def _segment_section(self, section: str) -> list[str]:
        """Рекурсивно дробит section до чанков <= max_tokens.

        Args:
            section (str): Текст одного раздела.

        Returns:
            list[str]: Список чанков.
        """
        if self._len(section) <= self.max_tokens:
            return [section]

        parts = self._EMPTY_RE.split(section)
        if len(parts) > 1:
            return [c for p in parts for c in self._segment_section(p)]

        if self.split_sentences:
            segs, buf = [], ""
            for sent in self._split_sentences(section):
                tentative = f"{buf} {sent}".strip() if buf else sent
                if self._len(tentative) <= self.max_tokens:
                    buf = tentative
                else:
                    if buf:
                        segs.append(buf)
                    buf = sent
            if buf:
                segs.append(buf)
            if segs and all(self._len(s) <= self.max_tokens for s in segs):
                return segs

        return list(self._token_window(section))

    def _split_sentences(self, text: str) -> list[str]:
        """Разделяет текст на предложения.

        Args:
            text (str): Входной текст.

        Returns:
            list[str]: Список предложений.
        """
        return [s.strip() for s in self._SENT_RE.split(text) if s.strip()]

    def _apply_overlap(
        self, chunks: list[tuple[str | None, str]]
    ) -> list[tuple[str | None, str]]:
        """Добавляет overlap-токены между чанками одного раздела.

        Args:
            chunks (list[tuple[str | None, str]]): Список чанков с заголовками.

        Returns:
            list[tuple[str | None, str]]: Чанки с overlap.
        """
        if not chunks:
            return []
        out: list[tuple[str | None, str]] = [chunks[0]]
        for (prev_hdr, prev_txt), (cur_hdr, cur_txt) in pairwise(chunks):
            if prev_hdr != cur_hdr:
                out.append((cur_hdr, cur_txt))
                continue
            tail = _encode(prev_txt)[-self.overlap :]
            merged = (tail + _encode(cur_txt))[: self.max_tokens]
            out.append((cur_hdr, _ENCODING.decode(merged)))
        return out

    def _token_window(self, text: str) -> Iterable[str]:
        """Делит текст на чанки по токенам фиксированного размера.

        Args:
            text (str): Исходный текст.

        Yields:
            str: Следующий чанк.
        """
        tokens = _encode(text)
        for i in range(0, len(tokens), self.max_tokens):
            yield _ENCODING.decode(tokens[i : i + self.max_tokens])

    def _extract_clause(self, text: str) -> str | None:
        """Извлекает номер пункта (например, '5.2') из начала строки.

        Args:
            text (str): Входной текст чанка.

        Returns:
            str | None: Найденный номер или None.
        """
        m = self._CLAUSE_RE.match(text.lstrip())
        return m.group(1) if m else None

    def _len(self, text: str) -> int:
        """Вычисляет количество токенов в тексте.

        Args:
            text (str): Входной текст.

        Returns:
            int: Количество токенов.
        """
        return len(_encode(text))

    def _dedup(self, chunks: list[dict]) -> list[dict]:
        """Удаляет дубликаты чанков по MinHash.

        Args:
            chunks (list[dict]): Список чанков с мета.

        Returns:
            list[dict]: Уникальные чанки.
        """
        accepted, sigs = [], []
        for ch in chunks:
            mh = self._minhash(ch["text"])
            dup = next(
                (i for i, s in enumerate(sigs)
                 if mh.jaccard(s) >= self._DEDUP_THRESHOLD),
                None,
            )
            if dup is not None:
                logger.debug(
                    "Dedup: пропущен чанк",
                    idx=ch["chunk_idx"],
                    similar_to=accepted[dup]["chunk_idx"],
                )
                continue
            sigs.append(mh)
            accepted.append(ch)
        for i, ch in enumerate(accepted):
            ch["chunk_idx"] = i
        return accepted

    def _minhash(self, text: str) -> MinHash:
        """Создаёт MinHash-подпись текста.

        Args:
            text (str): Текст чанка.

        Returns:
            MinHash: Подпись.
        """
        mh = MinHash(num_perm=self._MINHASH_NUM_PERM)
        for sh in self._shingles(text):
            mh.update(sh.encode())
        return mh

    def _shingles(self, text: str) -> set[str]:
        """Выделяет шинглы из текста.

        Args:
            text (str): Исходный текст.

        Returns:
            set[str]: Набор шинглов.
        """
        words = re.findall(r"\w+", text.lower())
        if len(words) < self._SHINGLE_SIZE:
            return {" ".join(words)}
        return {
            " ".join(words[i : i + self._SHINGLE_SIZE])
            for i in range(len(words) - self._SHINGLE_SIZE + 1)
        }
