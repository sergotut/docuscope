"""Адаптер Qdrant.

Адаптер реализует протокол VectorStorePort и хранит каждый документ в отдельной
коллекции Qdrant. Позволяет вставлять эмбеддинги, выполнять гибридный поиск,
удалять коллекции и очищать просроченные данные.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Final

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.exceptions import VectorStoreError
from app.core.ports.vector_store import VectorStorePort
from app.core.settings.qdrant import QdrantSettings

_RETRY: Final = dict(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=0.1, max=2),
    stop=stop_after_attempt(3),
)


class QdrantVectorStore(VectorStorePort):
    """Класс адаптера хранилища векторов на базе Qdrant."""

    def __init__(
        self,
        settings: QdrantSettings,
        client: QdrantClient | None = None,
    ) -> None:
        """Создаёт экземпляр адаптера.

        Args:
            settings (QdrantSettings): Настройки подключения к Qdrant.
            client (QdrantClient | None): Пользовательский клиент или None для
                создания нового клиента.
        """
        self._s = settings
        self._client = client or QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=settings.qdrant_timeout,
            prefer_grpc=False,
        )

    def upsert(
        self,
        doc_id: str,
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """Добавляет или обновляет векторы документа.

        Args:
            doc_id (str): Идентификатор документа.
            vectors (list[list[float]]): Список эмбеддингов.
            metadatas (list[dict]): Метаданные для каждого эмбеддинга.
        """
        collection = self._col(doc_id)
        self._ensure_collection(collection)

        points = [
            qm.PointStruct(id=i, vector=v, payload=meta)
            for i, (v, meta) in enumerate(zip(vectors, metadatas))
        ]
        self._upsert_batch(collection, points)

    def hybrid_search(
        self,
        doc_id: str,
        query: str,
        top_k: int,
    ) -> list[qm.ScoredPoint]:
        """Выполняет гибридный поиск по документу.

        Args:
            doc_id (str): Идентификатор документа.
            query (str): Текстовый запрос.
            top_k (int): Максимальное число результатов.

        Returns:
            list[qm.ScoredPoint]: Найденные точки с оценкой сходства.
        """
        sr = qm.SearchRequest(
            vector=query,
            limit=top_k,
            with_payload=True,
            with_vector=False,
        )
        try:
            return self._client.search(
                collection_name=self._col(doc_id),
                search_request=sr,
            )
        except Exception as exc:  # noqa: BLE001
            raise VectorStoreError(str(exc)) from exc

    def drop(self, doc_id: str) -> None:
        """Удаляет коллекцию, связанную с документом.

        Args:
            doc_id (str): Идентификатор документа.
        """
        try:
            self._client.delete_collection(self._col(doc_id))
        except Exception as exc:  # noqa: BLE001
            raise VectorStoreError(str(exc)) from exc

    def cleanup_expired(self, ttl_hours: int) -> None:
        """Удаляет коллекции старше ttl_hours.

        Args:
            ttl_hours (int): Время жизни коллекции в часах.
        """
        expire_at = _dt.datetime.utcnow() - _dt.timedelta(hours=ttl_hours)
        for col in self._client.get_collections().collections:
            if not col.name.startswith(self._s.qdrant_collection_prefix):
                # не наша коллекция
                continue

            created = (
                _dt.datetime.fromisoformat(col.status.created.rstrip("Z"))
                if col.status.created
                else None
            )
            if created and created < expire_at:
                self._client.delete_collection(col.name)

    def is_healthy(self) -> bool:  # noqa: D401
        """Короткий health-check.

        Returns:
            bool: True, если ответ успешен.
        """
        try:
            return self._client.get_collections().status == "ok"
        except Exception:
            return False

    def _col(self, doc_id: str) -> str:
        """Преобразует doc_id в имя коллекции.

        Args:
            doc_id (str): Идентификатор документа.

        Returns:
            str: Имя коллекции.
        """
        return f"{self._s.qdrant_collection_prefix}{doc_id}"

    def _ensure_collection(self, name: str) -> None:
        """Создаёт коллекцию, если она отсутствует.

        Args:
            name (str): Имя коллекции.
        """
        names = {c.name for c in self._client.get_collections().collections}
        if name not in names:
            self._client.create_collection(
                collection_name=name,
                vectors_config=qm.VectorParams(
                    size=1536,
                    distance=qm.Distance.COSINE,
                ),
            )

    @retry(**_RETRY)
    def _upsert_batch(self, collection: str, points: list[qm.PointStruct]) -> None:
        """Вызывает Qdrant *upsert* с автоматическим ретраем.

        Args:
            collection (str): Имя коллекции.
            points (list[qm.PointStruct]): Точки для вставки.
        """
        try:
            self._client.upsert(collection_name=collection, points=points)
        except Exception as exc:
            raise VectorStoreError(str(exc)) from exc
