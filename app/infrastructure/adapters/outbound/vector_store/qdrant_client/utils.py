"""Внутренние утилиты и константы для Qdrant-адаптера."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

import structlog

from app.domain.model.collections import CollectionName
from app.domain.model.retrieval import SearchHit
from app.domain.model.vector_store import FieldName

__all__ = [
    "DENSE_VECTOR_NAME",
    "SPARSE_VECTOR_NAME",
    "PAYLOAD_CREATED_AT_TS",
    "META_POINT_ID",
    "PAYLOAD_COLLECTION_CREATED_AT_TS",
    "rrf_merge",
    "ready_hits",
    "as_collection_name",
    "as_field_name",
]


logger = structlog.get_logger(__name__)

# Именованные пространства векторов в Qdrant.
DENSE_VECTOR_NAME: Final[str] = "dense"
SPARSE_VECTOR_NAME: Final[str] = "sparse"

# Ключ в payload с отметкой времени вставки (epoch seconds).
PAYLOAD_CREATED_AT_TS: Final[str] = "_created_at_ts"

# Служебная «мета-точка» коллекции и её ключ времени создания.
META_POINT_ID: Final[str] = "__collection_meta__"
PAYLOAD_COLLECTION_CREATED_AT_TS: Final[str] = "_collection_created_at_ts"


def as_collection_name(value: CollectionName | str) -> str:
    """Возвращает нормализованное имя коллекции.

    Если передана строка — валидирует через CollectionName. При ошибке
    пишет предупреждение и возвращает исходную строку (fallback).

    Args:
        value (CollectionName | str): Имя коллекции.

    Returns:
        str: Строковое имя коллекции.
    """
    if isinstance(value, CollectionName):
        return str(value)
    try:
        return str(CollectionName(value))
    except ValueError as exc:
        logger.warning(
            "Qdrant: invalid collection name; fallback to raw", error=str(exc)
        )
        return value


def as_field_name(value: FieldName | str) -> str:
    """Возвращает нормализованное имя поля payload.

    Если передана строка — валидирует через FieldName. При ошибке пишет
    предупреждение и возвращает исходную строку (fallback).

    Args:
        value (FieldName | str): Имя поля.

    Returns:
        str: Строковое имя поля.
    """
    if isinstance(value, FieldName):
        return str(value)
    try:
        return str(FieldName(value))
    except ValueError as exc:
        logger.warning("Qdrant: invalid field name; fallback to raw", error=str(exc))
        return value


def rrf_merge(
    dense: Iterable[SearchHit],
    sparse: Iterable[SearchHit],
    *,
    rrf_k: int,
    top_k: int,
) -> list[SearchHit]:
    """Сливает два ранжированных списка по Reciprocal Rank Fusion.

    Итоговый счёт: sum(1 / (rrf_k + rank)).

    Args:
        dense (Iterable[SearchHit]): Результаты dense-поиска.
        sparse (Iterable[SearchHit]): Результаты sparse-поиска.
        rrf_k (int): Сглаживающая константа RRF.
        top_k (int): Сколько результатов вернуть.

    Returns:
        list[SearchHit]: Список лучших результатов после слияния.
    """
    # Материализуем итераторы, чтобы безопасно итерироваться несколько раз.
    dense_list = list(dense)
    sparse_list = list(sparse)

    def ranks(items: list[SearchHit]) -> dict[str, int]:
        return {h.id: i + 1 for i, h in enumerate(items)}

    rd = ranks(dense_list)
    rs = ranks(sparse_list)

    all_ids = set(rd) | set(rs)
    dense_by = {h.id: h for h in dense_list}
    sparse_by = {h.id: h for h in sparse_list}

    merged: list[SearchHit] = []
    for pid in all_ids:
        score = 0.0
        if pid in rd:
            score += 1.0 / (rrf_k + rd[pid])
        if pid in rs:
            score += 1.0 / (rrf_k + rs[pid])

        base = dense_by.get(pid) or sparse_by.get(pid)
        merged.append(SearchHit(id=pid, score=score, payload=dict(base.payload)))

    merged.sort(key=lambda h: h.score, reverse=True)
    return merged[: max(top_k, 0)]


async def ready_hits(value: list[SearchHit]) -> list[SearchHit]:
    """Возвращает уже готовый список SearchHit.

    Args:
        value (list[SearchHit]): Готовые результаты.

    Returns:
        list[SearchHit]: Те же результаты.
    """
    return value
