"""Доменные модели для векторного хранилища.

Содержит результаты поиска и единицы загрузки (upsert) с базовой валидацией.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domain.exceptions import VectorStoreError
from app.domain.model.documents import ChunkId
from app.domain.model.retrieval import EmbeddingVector, SparseVector

__all__ = ["SearchHit", "UpsertPoint"]


@dataclass(slots=True, frozen=True)
class SearchHit:
    """Результат поиска.

    Attributes:
        id (str): Идентификатор точки или чанка.
        score (float): Релевантность результата. Больше — лучше.
        payload (dict[str, Any]): Произвольные метаданные результата.
    """

    id: str
    score: float
    payload: dict[str, Any]


@dataclass(slots=True, frozen=True)
class UpsertPoint:
    """Единица загрузки в хранилище.

    Объединяет dense, sparse и payload в одну атомарную структуру, чтобы
    избежать несогласованности параллельных списков при upsert.

    Attributes:
        id (ChunkId): Идентификатор точки.
        vector (EmbeddingVector | None): Dense-вектор, если задан.
        sparse (SparseVector | None): Разрежённый вектор, если задан.
        payload (dict[str, Any]): Метаданные точки.
    """

    id: ChunkId
    vector: EmbeddingVector | None
    sparse: SparseVector | None
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        """Проверяет, что задан хотя бы один тип вектора.

        Raises:
            VectorStoreError: Если vector и sparse одновременно отсутствуют.
        """
        if self.vector is None and self.sparse is None:
            msg = "Должен быть задан vector или sparse (хотя бы один)."
            raise VectorStoreError(msg)
