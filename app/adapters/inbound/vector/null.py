"""Null-обёртка для векторного хранилища."""

import structlog

from app.core.ports import VectorStorePort

logger = structlog.get_logger(__name__)


class NullVectorStore(VectorStorePort):
    """Заглушка для векторного хранилища.

    Используется как фолбэк, если реальный векторный движок недоступен или не настроен.
    """

    def upsert(self, vectors, metadatas):
        """Заглушка метода сохранения векторов.

        Args:
            vectors: Список векторов.
            metadatas: Метаданные к каждому вектору.
        """
        logger.debug("Вызван NullVectorStore (фолбэк)")

    def hybrid_search(self, query, top_k):
        """Заглушка метода гибридного поиска.

        Args:
            query: Текстовый запрос.
            top_k: Кол-во результатов.

        Returns:
            list: Пустой список.
        """
        logger.debug("Вызван NullVectorStore (фолбэк)")
        return []

    def is_healthy(self) -> bool:
        """Всегда возвращает False (не используется в проде).

        Returns:
            bool: False
        """
        return False
