"""Адаптер Qdrant (AsyncQdrantClient).

Реализует VectorStorePort:
- upsert точек (dense и/или sparse);
- поиск dense и sparse;
- гибридный поиск с локальным RRF-слиянием;
- drop коллекции и health-report;
- очистку по TTL коллекций (по времени их создания).

Коллекция создаётся «на лету» и получает служебную мета-точку с временем
создания.
"""

from __future__ import annotations

import asyncio
from typing import Final, Sequence

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm

from app.domain.exceptions import VectorStoreError
from app.domain.model.diagnostics import VectorStoreHealthReport
from app.domain.model.documents import DocumentId
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
        ttl_concurrency: int = 8,
        default_distance: str = "cosine",
    ) -> None:
        """Создаёт клиент Qdrant.

        Args:
            host (str | None): Хост Qdrant (например, 127.0.0.1).
            port (int): Порт REST API.
            api_key (str | None): Ключ для Qdrant Cloud.
            timeout (int | None): Таймаут запросов, сек.
            default_distance (str): cosine | dot | euclid.
            ttl_concurrency (int): Ограничение параллелизма при TTL-очистке.
        """
        self._client = AsyncQdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            timeout=timeout,
        )
        self._distance = to_distance(default_distance)
        self._ttl_concurrency = ttl_concurrency

        base_url = f"{host}:{port}" if host else None
        logger.info(
            "QdrantVectorStore init",
            url=base_url,
            distance=self._distance.name,
        )

    async def upsert_points(
        self,
        doc_id: DocumentId,
        points: Sequence[UpsertPoint],
    ) -> None:
        """Добавляет или обновляет точки документа.

        Args:
            doc_id (DocumentId): Идентификатор коллекции.
            points (Sequence[UpsertPoint]): Точки с dense/sparse и payload.

        Raises:
            VectorStoreError: При ошибке Qdrant.
        """
        if not points:
            return

        try:
            dense_dim = next(
                (p.vector.dim for p in points if p.vector is not None), None
            )
            has_sparse = any(p.sparse is not None for p in points)

            await self._ensure_collection(doc_id, dense_dim, has_sparse)

            q_points = [to_point_struct(p, add_created_ts=True) for p in points]
            await self._client.upsert(
                collection_name=as_collection_name(str(doc_id)),
                points=q_points,
                wait=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant upsert failed", doc_id=str(doc_id))
            raise VectorStoreError(str(exc)) from exc

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
            doc_id (DocumentId): Идентификатор коллекции.
            query_vector (EmbeddingVector): Вектор запроса.
            top_k (int): Количество результатов.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """
        try:
            q_filter = to_filter(filter) if filter else None
            res = await self._client.search(
                collection_name=as_collection_name(str(doc_id)),
                query_vector={DENSE_VECTOR_NAME: list(query_vector.values)},
                with_payload=True,
                limit=top_k,
                query_filter=q_filter,
            )
            return [to_hit(pt) for pt in res]
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant vector_search failed", doc_id=str(doc_id))
            raise VectorStoreError(str(exc)) from exc

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
            doc_id (DocumentId): Идентификатор коллекции.
            query_sparse (SparseVector): Разрежённый вектор запроса.
            top_k (int): Количество результатов.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Найденные совпадения.
        """
        try:
            q_filter = to_filter(filter) if filter else None
            res = await self._client.search(
                collection_name=as_collection_name(str(doc_id)),
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
            logger.exception("Qdrant sparse_search failed", doc_id=str(doc_id))
            raise VectorStoreError(str(exc)) from exc

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

        Итоговый счёт равен сумме 1 / (rrf_k + rank) по веткам.

        Args:
            doc_id (DocumentId): Идентификатор коллекции.
            query_vector (EmbeddingVector | None): Dense-вектор запроса.
            query_sparse (SparseVector | None): Sparse-вектор запроса.
            top_k (int): Сколько результатов вернуть после слияния.
            per_branch_k (int): Кандидатов из каждой ветки.
            rrf_k (int): Константа RRF, сглаживающая ранги.
            filter (QueryFilter | None): Фильтр по payload.

        Returns:
            list[SearchHit]: Результаты после RRF-слияния.
        """
        dense_task = (
            self.vector_search(
                doc_id,
                query_vector=query_vector,  # type: ignore[arg-type]
                top_k=per_branch_k,
                filter=filter,
            )
            if query_vector is not None
            else ready_hits([])
        )
        sparse_task = (
            self.sparse_search(
                doc_id,
                query_sparse=query_sparse,  # type: ignore[arg-type]
                top_k=per_branch_k,
                filter=filter,
            )
            if query_sparse is not None
            else ready_hits([])
        )

        dense_hits, sparse_hits = await dense_task, await sparse_task
        return rrf_merge(dense_hits, sparse_hits, rrf_k=rrf_k, top_k=top_k)

    async def drop(self, doc_id: DocumentId) -> None:
        """Удаляет коллекцию документа.

        Args:
            doc_id (DocumentId): Идентификатор коллекции.
        """
        try:
            name = as_collection_name(str(doc_id))
            if await self._client.collection_exists(name):
                await self._client.delete_collection(name)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant drop failed", doc_id=str(doc_id))
            raise VectorStoreError(str(exc)) from exc

    async def cleanup_expired(self, ttl_hours: int) -> None:
        """Удаляет коллекции, если они старше TTL по времени создания.

        Время создания берётся из служебной мета-точки __collection_meta__.
        Очистка выполняется параллельно с ограничением по семафору.

        Args:
            ttl_hours (int): Порог в часах.
        """
        try:
            cols = await self._client.get_collections()
            if not cols.collections or ttl_hours <= 0:
                return

            from datetime import UTC, datetime

            now_ts = int(datetime.now(tz=UTC).timestamp())
            threshold = ttl_hours * 3600

            sem = asyncio.Semaphore(self._ttl_concurrency)

            async def _maybe_drop(name: str) -> None:
                async with sem:
                    try:
                        meta = await self._client.retrieve(
                            collection_name=name,
                            ids=[META_POINT_ID],
                            with_payload=True,
                            with_vectors=False,
                        )
                        if not meta:
                            logger.debug(
                                "Qdrant: skip ttl cleanup: no meta point",
                                collection=name,
                            )
                            return

                        payload = getattr(meta[0], "payload", {}) or {}
                        created = payload.get(PAYLOAD_COLLECTION_CREATED_AT_TS)

                        if not isinstance(created, (int, float)):
                            logger.debug(
                                "Qdrant: skip ttl cleanup: invalid meta payload",
                                collection=name,
                                payload=payload,
                            )
                            return

                        if (now_ts - int(created)) >= threshold:
                            await self._client.delete_collection(name)
                            logger.info(
                                "Qdrant collection dropped (ttl by creation time)",
                                collection=name,
                            )
                    except Exception as col_exc:  # noqa: BLE001
                        logger.warning(
                            "Qdrant: ttl check failed for collection",
                            collection=name,
                            error=str(col_exc),
                        )

            await asyncio.gather(
                *(_maybe_drop(col.name) for col in cols.collections),
                return_exceptions=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Qdrant cleanup_expired failed", error=str(exc))
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
        doc_id: DocumentId,
        dense_dim: int | None,
        need_sparse: bool,
    ) -> None:
        """Создаёт коллекцию при отсутствии и ставит мета-точку.

        Args:
            doc_id (DocumentId): Имя коллекции.
            dense_dim (int | None): Размерность dense-вектора (если есть).
            need_sparse (bool): Требуется ли sparse-хранилище.
        """
        name = as_collection_name(str(doc_id))
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

        # Ставим служебную мета-точку с временем создания коллекции.
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
