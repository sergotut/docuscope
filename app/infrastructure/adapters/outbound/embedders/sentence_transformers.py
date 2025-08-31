"""Адаптер эмбеддеров на базе Sentence-Transformers.

Реализует EmbedderPort: асинхронный расчёт эмбеддингов, health-report и
метаданные (предпочтительный размер батча, dim, max_tokens).

Позволяет рассчитывать эмбеддинги с помощью любой модели из библиотеки
sentence-transformers. Поддерживает квантованные модели, асинхронный режим и
автоматическую перезагрузку локальных весов при изменении.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import structlog
import torch
from sentence_transformers import SentenceTransformer  # type: ignore[import]

from app.domain.model.diagnostics import EmbedderHealthReport
from app.domain.model.retrieval import EmbeddingBatch, EmbeddingVector
from app.domain.ports import EmbedderPort

__all__ = ["SentenceTransformersEmbedder"]

logger = structlog.get_logger(__name__)

# Допустимые строковые значения dtype → torch.dtype
_DTYPE_MAP: dict[str, torch.dtype] = {
    "float32": torch.float32,
    "fp32": torch.float32,
    "f32": torch.float32,
    "float16": torch.float16,
    "fp16": torch.float16,
    "f16": torch.float16,
    "bfloat16": torch.bfloat16,
    "bf16": torch.bfloat16,
}


class SentenceTransformersEmbedder(EmbedderPort):
    """Адаптер Sentence-Transformers.

    Attributes:
        model_name (str): Название модели или путь к локальной директории.
            device (str | None): Устройство инференса (cpu/cuda/mps).
            batch_size (int): Размер батча.
            dtype (str): Тип тензора ('float32', 'float16', 'bfloat16').
            quantized (bool): Загружать модель в 8-битном режиме (через bitsandbytes).
            max_tokens (int): Максимальное количество токенов.
            watch_local_dir (bool): Следить за локальной папкой модели и
                перезагружать при изменениях.
    """

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        batch_size: int = 1,
        dtype: str = "float32",
        quantized: bool = False,
        max_tokens: int | None = None,
        watch_local_dir: bool = True,
    ) -> None:
        """Создаёт адаптер Sentence-Transformers.

        Args:
            model_name (str): Название модели или путь к локальной директории.
            device (str | None): Устройство инференса (cpu/cuda/mps). Если
                None, выбирается автоматически.
            batch_size (int): Размер батча.
            dtype (str): Тип тензора ('float32', 'float16', 'bfloat16').
            quantized (bool): Загружать модель в 8-битном режиме (через bitsandbytes).
            max_tokens (int): Максимальное количество токенов.
            watch_local_dir (bool): Следить за локальной папкой модели и
                перезагружать при изменениях.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = int(batch_size)
        self.quantized = bool(quantized)
        self.watch_local_dir = bool(watch_local_dir)

        self._torch_dtype = self._parse_dtype(dtype)
        self._dtype_name = dtype
        self._max_tokens = int(max_tokens) if max_tokens is not None else 0

        self._model: SentenceTransformer
        self._model_mtime: float = 0.0
        self._dim: int = 0

        self._load_model()
        logger.info(
            "SentenceTransformers init",
            model=self.model_name,
            device=self.device,
            quantized=self.quantized,
            dim=self._dim,
            max_tokens=self._max_tokens,
            dtype=self._dtype_name,
            torch_dtype=str(self._torch_dtype).split(".")[-1],
        )

    async def embed(
        self,
        *,
        texts: list[str],
    ) -> EmbeddingBatch:
        """Вычисляет эмбеддинги для набора строк.

        Args:
            texts (list[str]): Список входных строк.

        Returns:
            EmbeddingBatch: Батч эмбеддингов в исходном порядке.
        """
        if not texts:
            return EmbeddingBatch(vectors=())

        self._reload_if_changed()
        logger.debug("ST embed request", count=len(texts))

        loop = asyncio.get_running_loop()
        arr: Any = await loop.run_in_executor(
            None,
            lambda: self._model.encode(
                texts,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
                device=self.device,
            ),
        )

        vectors = tuple(
            EmbeddingVector(values=tuple(float(x) for x in row.tolist()))
            for row in arr  # type: ignore[attr-defined]
        )

        if self._dim == 0 and vectors:
            self._dim = vectors[0].dim
            logger.info("ST embedding dim detected", dim=self._dim)

        return EmbeddingBatch(vectors=vectors)

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если модель загружена и устройство валидно.
        """
        try:
            return self._dim > 0 and await self._device_ok()
        except Exception:  # noqa: BLE001
            return False

    async def health(self) -> EmbedderHealthReport:
        """Подробный health-репорт.

        Returns:
            EmbedderHealthReport: Метаинформация о состоянии эмбеддера.
        """
        try:
            version = getattr(
                __import__("sentence_transformers"), "__version__", "unknown"
            )
        except Exception:  # noqa: BLE001
            version = "unknown"

        return {
            "model": self.model_name,
            "dim": self._dim,
            "framework": "sentence-transformers",
            "device": self.device,
            "version": version,
        }

    @property
    def preferred_batch_size(self) -> int:
        """Предпочтительный размер батча.

        Returns:
            int: Количество строк на один вызов embed.
        """
        return self.batch_size

    @property
    def embedding_dim(self) -> int:
        """Размерность выходного эмбеддинга.

        Returns:
            int: Количество элементов в одном векторе.
        """
        return self._dim

    @property
    def max_tokens(self) -> int:
        """Максимальное количество токенов на вход.

        Returns:
            int: Ограничение длины входной строки.
        """
        return self._max_tokens

    def _load_model(self) -> None:
        """Загружает модель и обновляет метаинформацию.

        Применяет torch_dtype через model_kwargs, если не используется
        8-битная загрузка. При quantized=True параметр dtype игнорируется,
        о чём пишется в лог.
        """
        logger.info(
            "Loading SentenceTransformer",
            model=self.model_name,
            device=self.device,
            quantized=self.quantized,
            dtype=self._dtype_name,
        )

        extra_args: dict[str, object] = {}
        model_kwargs: dict[str, object] = {}

        if self.quantized:
            # 8-битная загрузка конфликтует с явным torch_dtype.
            extra_args = {"device_map": "auto", "load_in_8bit": True}
            if self._dtype_name.lower() not in ("float32", "fp32", "f32"):
                logger.debug(
                    "dtype is ignored in 8-bit mode",
                    requested=self._dtype_name,
                )
        else:
            model_kwargs = {"torch_dtype": self._torch_dtype}

        # Некоторые версии st не типизируют сторонние kwargs — подавим mypy.
        self._model = SentenceTransformer(  # type: ignore[call-arg]
            self.model_name,
            device=self.device,
            model_kwargs=model_kwargs or None,
            **extra_args,
        )

        self._dim = int(self._model.get_sentence_embedding_dimension())

        # Если max_tokens явно не задан, пробуем взять из модели,
        # иначе оставляем 512.
        if self._max_tokens <= 0:
            detected = getattr(self._model, "max_seq_length", None)
            self._max_tokens = int(detected) if isinstance(detected, int) else 512

        if os.path.isdir(self.model_name):
            self._model_mtime = Path(self.model_name).stat().st_mtime

        logger.info(
            "SentenceTransformer loaded",
            dim=self._dim,
            max_tokens=self._max_tokens,
        )

    def _reload_if_changed(self) -> None:
        """Перезагружает модель, если изменились локальные веса."""
        if not self.watch_local_dir or not os.path.isdir(self.model_name):
            return

        mtime = Path(self.model_name).stat().st_mtime
        if mtime > self._model_mtime:
            logger.info("ST: detected local changes, reloading model")
            self._load_model()

    async def _device_ok(self) -> bool:
        """Проверяет доступность запрошенного устройства.

        Returns:
            bool: True, если устройство доступно или не требуется.
        """
        if self.device.startswith("cuda"):
            return bool(torch.cuda.is_available())
        return True

    @staticmethod
    def _parse_dtype(name: str) -> torch.dtype:
        """Парсит строковый dtype в torch.dtype.

        Args:
            name (str): Имя типа: float32/float16/bfloat16 и алиасы.

        Returns:
            torch.dtype: Соответствующий тип. Для неизвестных значений
            возвращается torch.float32.
        """
        key = name.lower().strip()
        dtype = _DTYPE_MAP.get(key, torch.float32)

        if dtype is torch.float32 and key not in ("float32", "fp32", "f32"):
            logger.debug("unknown dtype, fallback to float32", requested=name)

        return dtype

    def _chunks(self, seq: list[str]) -> Iterator[list[str]]:
        """Разбивает входной список на батчи.

        Args:
            seq (list[str]): Список строк.

        Returns:
            Iterator[list[str]]: Итератор по батчам.
        """
        for i in range(0, len(seq), self.batch_size):
            yield seq[i : i + self.batch_size]
