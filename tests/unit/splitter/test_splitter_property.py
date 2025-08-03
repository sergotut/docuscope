"""Property-based тесты для ContractSplitter.

Проверяют корректность чанковки:
- Все чанки не превышают max_tokens.
- Всегда есть хотя бы один чанк.
- Dedup удаляет дубли.
- Результат стабилен при одинаковом входе.
"""

import tiktoken
from hypothesis import given, settings
from hypothesis import strategies as st

from app.utils.splitter import ContractSplitter


@given(st.text(min_size=1, max_size=4000))
@settings(max_examples=50, deadline=None)
def test_chunks_within_limits(txt: str) -> None:
    """Проверяет: любой текст → чанки ≤ max_tokens и ≥ 1.

    Args:
        txt (str): Случайный Unicode-текст.
    """
    splitter = ContractSplitter(max_tokens=128, overlap=8)
    chunks = splitter.split(txt, {})
    assert chunks, "Должен быть хотя бы один чанк"

    enc = tiktoken.get_encoding("cl100k_base")
    for ch in chunks:
        assert len(enc.encode(ch["text"])) <= splitter.max_tokens


@given(st.lists(st.text(min_size=10, max_size=100), min_size=3, max_size=10))
@settings(max_examples=25, deadline=None)
def test_dedup_removes_duplicates(chunks: list[str]) -> None:
    """Проверяет, что дублированные куски удаляются dedup-логикой."""
    duplicated = "\n\n".join(chunks + chunks)
    splitter = ContractSplitter(max_tokens=128, overlap=0)
    result = splitter.split(duplicated)
    texts = [ch["text"] for ch in result]
    assert len(texts) <= len(chunks) + 2, "Дубликаты не были удалены"


@given(st.text(min_size=1, max_size=4000))
@settings(max_examples=25, deadline=None)
def test_split_is_idempotent(txt: str) -> None:
    """Гарантирует стабильность: один и тот же вход → одинаковый выход."""
    splitter = ContractSplitter(max_tokens=128, overlap=8)
    result1 = splitter.split(txt)
    result2 = splitter.split(txt)
    assert result1 == result2, "Результат не детерминирован"
