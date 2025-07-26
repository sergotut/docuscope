"""
Модуль для работы с векторной базой данных Qdrant.

Используется для хранения и поиска эмбеддингов текстовых фрагментов документов.
"""

from typing import Dict, List

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import UnexpectedResponse

logger = structlog.get_logger()


class QdrantVectorStore:
    """
    Адаптер для взаимодействия с векторным хранилищем Qdrant.

    Автоматически создает коллекцию для хранения векторов, если она отсутствует.
    Позволяет массово добавлять векторы и связанные payload-данные.
    """

    def __init__(self, url: str, collection: str = "documents", dim: int = 768):
        """
        Инициализация клиента Qdrant и подготовка коллекции.

        Args:
            url (str): Адрес Qdrant-сервера.
            collection (str, optional): Имя коллекции для хранения векторов
                (по умолчанию "documents").
            dim (int, optional): Размерность вектора (по умолчанию 768).

        Raises:
            Exception: Если не удалось проверить или создать коллекцию.
        """
        self.collection = collection
        self.dim = dim
        self.client = QdrantClient(url=url)

        try:
            collections = self.client.get_collections().collections
            existing = [c.name for c in collections]
            if self.collection not in existing:
                logger.warning("qdrant_collection_missing", collection=self.collection)
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=rest.VectorParams(size=self.dim, distance="Cosine"),
                )
                logger.info("qdrant_collection_created", collection=self.collection)
        except Exception as e:
            logger.error("qdrant_collection_check_failed", error=str(e))
            raise
        logger.info(
            "qdrant_client_ready",
            url=url,
            collection=self.collection
        )

    def upsert(self, vectors: List[List[float]], payloads: List[Dict]):
        """
        Добавляет/обновляет вектора с привязанными payload-данными в коллекции Qdrant.

        Args:
            vectors (List[List[float]]): Список векторов (списков float).
            payloads (List[Dict]): Список словарей с метаданными для каждого вектора.

        Raises:
            ValueError: Если количество векторов и payload не совпадает.
            UnexpectedResponse: Если Qdrant вернул ошибку.
        """
        if len(vectors) != len(payloads):
            raise ValueError("vectors and payloads length must match")

        points = [
            rest.PointStruct(id=i, vector=v, payload=payloads[i])
            for i, v in enumerate(vectors)
        ]

        try:
            self.client.upload_points(
                collection_name=self.collection,
                points=points,
                wait=True,
            )
            logger.debug("qdrant_upsert", count=len(points))
        except UnexpectedResponse as e:
            logger.error("qdrant_upsert_failed", error=str(e))
            raise
