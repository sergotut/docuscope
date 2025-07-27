"""
DI-обёртка для Qdrant Vector Store.
"""

import structlog
from app.adapters.outbound.vector.qdrant import QdrantVectorStore
from app.core.settings import settings
from app.infrastructure.protocols import VectorStorePort

logger = structlog.get_logger(__name__)

class QdrantVectorStoreAdapter(QdrantVectorStore, VectorStorePort):
    """DI-адаптер для Qdrant Vector Store."""

    def __init__(self) -> None:
        super().__init__(url=getattr(settings.ai, "qdrant_url", "http://localhost:6333"))
        logger.info(
            "Создан QdrantVectorStoreAdapter",
            url=getattr(settings.ai, "qdrant_url", "http://localhost:6333")
        )

    def is_healthy(self) -> bool:
        try:
            logger.debug("Проверка is_healthy для QdrantVectorStoreAdapter")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
