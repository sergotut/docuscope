"""Порт векторного хранилища для RAG (dense + sparse + RRF).

Поддерживает:
- upsert точек с dense и/или sparse векторами;
- чисто векторный поиск (dense);
- чисто разрежённый поиск (sparse);
- гибридный поиск с RRF (слияние списков);
- очистку по TTL, удаление коллекции, health‑check.

Интерфейс включает синхронные и асинхронные методы.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True)
class SearchHit:
    """Результат поиска.

    Attributes:
        id (str): Идентификатор точки/чанка.
        score (float): Релевантность (чем больше, тем лучше).
        payload (dict[str, Any]): Метаданные.
    """

    id: str
    score: float
    payload: dict[str, Any]


@dataclass(slots=True)
class SparseVector:
    """Разрежённый вектор (TF‑IDF/BM25/SPLADE‑подобный).

    Attributes:
        indices (list[int]): Индексы ненулевых координат.
        values (list[float]): Значения весов по соответствующим индексам.
    """

    indices: list[int]
    values: list[float]


@runtime_checkable
class VectorStorePort(Protocol):
    """Порт векторного хранилища для RAG."""

    def upsert(
        self,
        doc_id: str,
        vectors: Sequence[Sequence[float]] | None,
        metadatas: Sequence[Mapping[str, Any]],
        *,
        sparse: Sequence[SparseVector] | None = None,
        ids: Sequence[str | int] | None = None,
    ) -> None:
        """Добавляет/обновляет точки документа.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            vectors (Sequence[Sequence[float]] | None): Dense‑вектора точек.
                Может быть None, если грузим только sparse.
            metadatas (Sequence[Mapping[str, Any]]): Метаданные для точек.
            sparse (Sequence[SparseVector] | None): Разрежённые вектора.
                Может быть None, если грузим только dense.
            ids (Sequence[str | int] | None): Явные идентификаторы точек.
        """

    async def upsert_async(
        self,
        doc_id: str,
        vectors: Sequence[Sequence[float]] | None,
        metadatas: Sequence[Mapping[str, Any]],
        *,
        sparse: Sequence[SparseVector] | None = None,
        ids: Sequence[str | int] | None = None,
    ) -> None:
        """Асинхронный upsert.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            vectors (Sequence[Sequence[float]] | None): Dense‑вектора точек.
                Может быть None, если грузим только sparse.
            metadatas (Sequence[Mapping[str, Any]]): Метаданные для точек.
            sparse (Sequence[SparseVector] | None): Разрежённые вектора.
                Может быть None, если грузим только dense.
            ids (Sequence[str | int] | None): Явные идентификаторы точек.
        """

    def vector_search(
        self,
        doc_id: str,
        query_vector: Sequence[float],
        top_k: int,
        *,
        filter: Mapping[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Поиск по dense‑вектору.

        По контракту score: больше → лучше.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            query_vector (Sequence[float]): Вектор запроса.
            top_k (int): Количество результатов.
            filter (Mapping[str, Any] | None): Фильтр по payload
                (например, {"page": {"$gte": 2}}).

        Returns:
            list[SearchHit]: Найденные совпадения.
        """

    async def vector_search_async(
        self,
        doc_id: str,
        query_vector: Sequence[float],
        top_k: int,
        *,
        filter: Mapping[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Асинхронный поиск по dense‑вектору.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            query_vector (Sequence[float]): Вектор запроса.
            top_k (int): Количество результатов.
            filter (Mapping[str, Any] | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """

    # -------------------------------------------------------------- sparse search
    def sparse_search(
        self,
        doc_id: str,
        query_sparse: SparseVector,
        top_k: int,
        *,
        filter: Mapping[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Поиск по sparse‑вектору.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            query_sparse (SparseVector): Разрежённый вектор запроса.
            top_k (int): Количество результатов.
            filter (Mapping[str, Any] | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """

    async def sparse_search_async(
        self,
        doc_id: str,
        query_sparse: SparseVector,
        top_k: int,
        *,
        filter: Mapping[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Асинхронный поиск по sparse‑вектору.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            query_sparse (SparseVector): Разрежённый вектор запроса.
            top_k (int): Количество результатов.
            filter (Mapping[str, Any] | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """

    def hybrid_search_rrf(
        self,
        doc_id: str,
        *,
        query_vector: Sequence[float] | None,
        query_sparse: SparseVector | None,
        top_k: int,
        per_branch_k: int = 100,
        rrf_k: int = 60,
        filter: Mapping[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Гибридный поиск: dense + sparse, слияние по RRF.

        Итоговый счёт = сумма 1 / (k + rank) по веткам (RRF).

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            query_vector (Sequence[float] | None): Dense‑вектор запроса.
            query_sparse (SparseVector | None): Sparse‑вектор запроса.
            top_k (int): Сколько результатов вернуть после слияния.
            per_branch_k (int): Кандидатов из каждой ветки.
            rrf_k (int): Константа RRF, сглаживает ранги.
            filter (Mapping[str, Any] | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Результаты, отсортированные по RRF‑скорингу.
        """

    async def hybrid_search_rrf_async(
        self,
        doc_id: str,
        *,
        query_vector: Sequence[float] | None,
        query_sparse: SparseVector | None,
        top_k: int,
        per_branch_k: int = 100,
        rrf_k: int = 60,
        filter: Mapping[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Асинхронная версия гибридного поиска RRF.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
            query_vector (Sequence[float] | None): Dense‑вектор запроса.
            query_sparse (SparseVector | None): Sparse‑вектор запроса.
            top_k (int): Сколько результатов вернуть после слияния.
            per_branch_k (int): Кандидатов из каждой ветки.
            rrf_k (int): Константа RRF, сглаживает ранги.
            filter (Mapping[str, Any] | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Результаты, отсортированные по RRF‑скорингу.
        """

    def drop(self, doc_id: str) -> None:
        """Удаляет коллекцию документа.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
        """

    async def drop_async(self, doc_id: str) -> None:
        """Асинхронное удаление коллекции документа.

        Args:
            doc_id (str): Идентификатор документа/коллекции.
        """

    def cleanup_expired(self, ttl_hours: int) -> None:
        """Удаляет устаревшие точки по TTL.

        Args:
            ttl_hours (int): Возраст данных (в часах), старше которого удалить.
        """

    async def cleanup_expired_async(self, ttl_hours: int) -> None:
        """Асинхронная очистка по TTL.

        Args:
            ttl_hours (int): Возраст данных (в часах), старше которого удалить.
        """

    def is_healthy(self) -> bool:
        """Короткий health‑check.

        Returns:
            bool: True, если хранилище доступно.
        """
