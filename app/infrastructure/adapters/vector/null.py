"""Null-обёртка для векторного хранилища."""

import structlog

from app.infrastructure.protocols import VectorStorePort

logger = structlog.get_logger(__name__)


class NullVectorStore(VectorStorePort):
    """Заглушка для векторного хранилища."""

    def upsert(self, vectors, metadatas):
        logger.debug("Вызван NullVectorStore (фолбэк)")

    def hybrid_search(self, query, top_k):
        logger.debug("Вызван NullVectorStore (фолбэк)")
        return []

    def is_healthy(self) -> bool:
        return False
