"""Порт (интерфейс) векторного хранилища для RAG.

Поддерживает:
- upsert точек (через доменную модель UpsertPoint);
- чисто векторный поиск (dense);
- чисто разрежённый поиск (sparse);
- гибридный поиск с RRF (слияние списков);
- очистку по TTL, удаление коллекции, health‑check.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import VectorStoreHealthReport
from app.domain.model.documents import DocumentId
from app.domain.model.retrieval import (
    EmbeddingVector,
    QueryFilter,
    SearchHit,
    SparseVector,
    UpsertPoint,
)

__all__ = ["VectorStorePort"]


@runtime_checkable
class VectorStorePort(Protocol):
    """Абстрактный порт векторного хранилища.

    Интерфейс покрывает операции записи точек, варианты поиска (dense, sparse,
    гибридный RRF), удаление данных и проверку состояния.
    """

    async def upsert_points(
        self,
        doc_id: DocumentId,
        points: Sequence[UpsertPoint],
    ) -> None:
        """Добавляет или обновляет точки документа.

        Args:
            doc_id (DocumentId): Идентификатор документа/коллекции.
            points (Sequence[UpsertPoint]): Точки с dense/sparse и payload.
        """
        ...

    async def vector_search(
        self,
        doc_id: DocumentId,
        query_vector: EmbeddingVector,
        top_k: int,
        *,
        filter: QueryFilter | None = None,
    ) -> list[SearchHit]:
        """Поиск по dense-вектору.

        Args:
            doc_id (DocumentId): Идентификатор документа/коллекции.
            query_vector (EmbeddingVector): Вектор запроса.
            top_k (int): Количество результатов.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """
        ...

    async def sparse_search(
        self,
        doc_id: DocumentId,
        query_sparse: SparseVector,
        top_k: int,
        *,
        filter: QueryFilter | None = None,
    ) -> list[SearchHit]:
        """Поиск по sparse-вектору.

        Args:
            doc_id (DocumentId): Идентификатор документа/коллекции.
            query_sparse (SparseVector): Разрежённый вектор запроса.
            top_k (int): Количество результатов.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """
        ...

    async def hybrid_search_rrf(
        self,
        doc_id: DocumentId,
        *,
        query_vector: EmbeddingVector | None,
        query_sparse: SparseVector | None,
        top_k: int,
        per_branch_k: int = 100,
        rrf_k: int = 60,
        filter: QueryFilter | None = None,
    ) -> list[SearchHit]:
        """Гибридный поиск: dense + sparse, слияние по RRF.

        Итоговый счёт = сумма 1 / (k + rank) по веткам.

        Args:
            doc_id (DocumentId): Идентификатор документа/коллекции.
            query_vector (EmbeddingVector | None): Dense-вектор запроса.
            query_sparse (SparseVector | None): Sparse-вектор запроса.
            top_k (int): Сколько результатов вернуть после слияния.
            per_branch_k (int): Кандидатов из каждой ветки.
            rrf_k (int): Константа RRF, сглаживает ранги.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Результаты, отсортированные по RRF-скорингу.
        """
        ...

    async def drop(self, doc_id: DocumentId) -> None:
        """Удаляет коллекцию документа.

        Args:
            doc_id (DocumentId): Идентификатор документа/коллекции.
        """
        ...

    async def cleanup_expired(self, ttl_hours: int) -> None:
        """Удаляет устаревшие коллекции по TTL.

        Args:
            ttl_hours (int): Возраст коллекций (в часах), старше которого удалить.
        """
        ...

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если хранилище доступно.
        """
        ...

    async def health(self) -> VectorStoreHealthReport:
        """Подробный health-репорт.

        Returns:
            VectorStoreHealthReport: Метаинформация о состоянии хранилища.
        """
        ...