"""Адаптер Qdrant (AsyncQdrantClient).

Реализует VectorStorePort:
- upsert точек (dense и/или sparse);
- поиск dense и sparse;
- гибридный поиск с локальным RRF-слиянием;
- drop коллекции и health-report.
Коллекция создаётся «на лету» и получает служебную мета-точку с временем
создания.
"""

from __future__ import annotations

import asyncio
from typing import Sequence

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm

from app.domain.exceptions import VectorStoreError
from app.domain.model.collections import CollectionName
from app.domain.model.diagnostics import VectorStoreHealthReport
from app.domain.model.retrieval import (
    EmbeddingVector,
    QueryFilter,
    SearchHit,
    SparseVector,
    UpsertPoint,
)
from app.domain.ports.vector_store import VectorStorePort
from .converters import to_distance, to_filter, to_hit, to_point_struct
from .utils import (
    DENSE_VECTOR_NAME,
    META_POINT_ID,
    PAYLOAD_COLLECTION_CREATED_AT_TS,
    SPARSE_VECTOR_NAME,
    as_collection_name,
    ready_hits,
    rrf_merge,
)

__all__ = ["QdrantVectorStore"]

logger = structlog.get_logger(__name__)


class QdrantVectorStore(VectorStorePort):
    """Адаптер векторного хранилища Qdrant (AsyncQdrantClient).

    Attributes:
        _client (AsyncQdrantClient): Асинхронный клиент Qdrant.
        _distance (qm.Distance): Метрика для dense-векторов по умолчанию.
    """

    _client: AsyncQdrantClient
    _distance: qm.Distance

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int = 6333,
        api_key: str | None = None,
        timeout: int | None = None,
        default_distance: str = "cosine",
    ) -> None:
        """Создаёт клиент Qdrant.

        Args:
            host (str | None): Хост Qdrant (например, 127.0.0.1).
            port (int): Порт REST API.
            api_key (str | None): Ключ для Qdrant Cloud.
            timeout (int | None): Таймаут запросов, сек.
            default_distance (str): cosine | dot | euclid.
        """
        self._client = AsyncQdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            timeout=timeout,
        )
        self._distance = to_distance(default_distance)

        base_url = f"{host}:{port}" if host else None
        logger.info(
            "QdrantVectorStore init",
            url=base_url,
            distance=self._distance.name,
        )

    async def upsert_points(
        self,
        collection: CollectionName,
        points: Sequence[UpsertPoint],
    ) -> None:
        """Добавляет или обновляет точки в коллекции.

        Args:
            collection (CollectionName): Имя коллекции.
            points (Sequence[UpsertPoint]): Точки с dense/sparse и payload.

        Raises:
            VectorStoreError: При ошибке Qdrant.
        """
        if not points:
            return
        try:
            cname = as_collection_name(str(collection))
            dense_dim = next(
                (p.vector.dim for p in points if p.vector is not None),
                None,
            )
            has_sparse = any(p.sparse is not None for p in points)

            await self._ensure_collection(collection, dense_dim, has_sparse)

            q_points = [to_point_struct(p, add_created_ts=True) for p in points]
            await self._client.upsert(
                collection_name=cname,
                points=q_points,
                wait=True,
            )

            logger.info(
                "qdrant upsert ok",
                collection=cname,
                points=len(points),
                dense_dim=dense_dim,
                has_sparse=has_sparse,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant upsert failed", collection=str(collection))
            raise VectorStoreError(str(exc)) from exc

    async def vector_search(
        self,
        collection: CollectionName,
        query_vector: EmbeddingVector,
        top_k: int,
        *,
        filter: QueryFilter | None = None,
    ) -> list[SearchHit]:
        """Поиск по dense-вектору.

        Args:
            collection (CollectionName): Имя коллекции.
            query_vector (EmbeddingVector): Вектор запроса.
            top_k (int): Количество результатов.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """
        try:
            cname = as_collection_name(str(collection))
            q_filter = to_filter(filter) if filter else None
            res = await self._client.search(
                collection_name=cname,
                query_vector={DENSE_VECTOR_NAME: list(query_vector.values)},
                with_payload=True,
                limit=top_k,
                query_filter=q_filter,
            )
            return [to_hit(pt) for pt in res]
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant vector_search failed", collection=str(collection))
            raise VectorStoreError(str(exc)) from exc

    async def sparse_search(
        self,
        collection: CollectionName,
        query_sparse: SparseVector,
        top_k: int,
        *,
        filter: QueryFilter | None = None,
    ) -> list[SearchHit]:
        """Поиск по sparse-вектору.

        Args:
            collection (CollectionName): Имя коллекции.
            query_sparse (SparseVector): Разрежённый вектор запроса.
            top_k (int): Количество результатов.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """
        try:
            cname = as_collection_name(str(collection))
            q_filter = to_filter(filter) if filter else None
            res = await self._client.search(
                collection_name=cname,
                query_vector={
                    SPARSE_VECTOR_NAME: qm.SparseVector(
                        indices=list(query_sparse.indices),
                        values=list(query_sparse.values),
                    )
                },
                with_payload=True,
                limit=top_k,
                query_filter=q_filter,
            )
            return [to_hit(pt) for pt in res]
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Qdrant sparse_search failed",
                collection=str(collection)
            )
            raise VectorStoreError(str(exc)) from exc

    async def hybrid_search_rrf(
        self,
        collection: CollectionName,
        *,
        query_vector: EmbeddingVector | None,
        query_sparse: SparseVector | None,
        top_k: int,
        per_branch_k: int = 100,
        rrf_k: int = 60,
        filter: QueryFilter | None = None,
    ) -> list[SearchHit]:
        """Гибридный поиск: dense + sparse, слияние по RRF.

        Итоговый счёт равен сумме 1 / (rrf_k + rank) по веткам.

        Args:
            collection (CollectionName): Имя коллекции.
            query_vector (EmbeddingVector | None): Dense-вектор запроса.
            query_sparse (SparseVector | None): Sparse-вектор запроса.
            top_k (int): Сколько результатов вернуть после слияния.
            per_branch_k (int): Кандидатов из каждой ветки.
            rrf_k (int): Константа RRF.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Результаты после RRF-слияния.
        """
        if query_vector is None and query_sparse is None:
            return []

        if top_k <= 0:
            return []

        if per_branch_k <= 0:
            per_branch_k = top_k

        dense_coro = (
            self.vector_search(
                collection,
                query_vector=query_vector,  # type: ignore[arg-type]
                top_k=per_branch_k,
                filter=filter,
            )
            if query_vector is not None
            else ready_hits([])
        )

        sparse_coro = (
            self.sparse_search(
                collection,
                query_sparse=query_sparse,  # type: ignore[arg-type]
                top_k=per_branch_k,
                filter=filter,
            )
            if query_sparse is not None
            else ready_hits([])
        )

        dense_hits, sparse_hits = await asyncio.gather(dense_coro, sparse_coro)
        return rrf_merge(dense_hits, sparse_hits, rrf_k=rrf_k, top_k=top_k)

    async def drop_collection(self, name: CollectionName) -> None:
        """Удаляет коллекцию Qdrant по имени.

        Операция идемпотентна: если коллекции нет, ошибок не возникает.

        Args:
            name (CollectionName): Имя коллекции.
        """
        cname = str(name)
        try:
            if await self._client.collection_exists(cname):
                await self._client.delete_collection(cname)
            logger.info("qdrant drop_collection done", collection=cname)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant drop_collection failed", collection=cname)
            raise VectorStoreError(str(exc)) from exc

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если Qdrant отвечает.
        """
        try:
            await self._client.get_collections()
            return True
        except Exception:  # noqa: BLE001
            return False

    async def health(self) -> VectorStoreHealthReport:
        """Подробный health-репорт.

        Returns:
            VectorStoreHealthReport: Версия, метрика и число коллекций.
        """
        try:
            version = await self._client.get_version()
            cols = await self._client.get_collections()
            count = len(cols.collections or [])
            return {
                "engine": "qdrant",
                "version": str(version),
                "distance": self._distance.name.lower(),
                "collections": count,
                "status": "ok",
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Qdrant health fail", error=str(exc))
            return {
                "engine": "qdrant",
                "version": "unknown",
                "distance": self._distance.name.lower(),
                "collections": 0,
                "status": "fail",
            }

    async def _ensure_collection(
        self,
        collection: CollectionName,
        dense_dim: int | None,
        need_sparse: bool,
    ) -> None:
        """Создаёт коллекцию при отсутствии и ставит мета-точку.

        Args:
            collection (CollectionName): Имя коллекции.
            dense_dim (int | None): Размерность dense-вектора (если есть).
            need_sparse (bool): Требуется ли sparse-хранилище.
        """
        if dense_dim is None and not need_sparse:
            raise VectorStoreError(
                "cannot create collection without vectors:"
                "dense and sparse are both missing"
            )
        name = as_collection_name(str(collection))

        if await self._client.collection_exists(name):
            return

        vectors_cfg: dict[str, qm.VectorParams] | None = None
        sparse_cfg: dict[str, qm.SparseVectorParams] | None = None

        if dense_dim is not None:
            vectors_cfg = {
                DENSE_VECTOR_NAME: qm.VectorParams(
                    size=dense_dim,
                    distance=self._distance,
                )
            }
        if need_sparse:
            sparse_cfg = {SPARSE_VECTOR_NAME: qm.SparseVectorParams()}

        await self._client.create_collection(
            collection_name=name,
            vectors_config=vectors_cfg or {},
            sparse_vectors_config=sparse_cfg or None,
        )

        from datetime import UTC, datetime

        created_ts = int(datetime.now(tz=UTC).timestamp())
        await self._client.upsert(
            collection_name=name,
            points=[
                qm.PointStruct(
                    id=META_POINT_ID,
                    payload={PAYLOAD_COLLECTION_CREATED_AT_TS: created_ts},
                )
            ],
            wait=True,
        )

        logger.info(
            "Qdrant collection created",
            collection=name,
            dense_dim=dense_dim,
            sparse=need_sparse,
        )
