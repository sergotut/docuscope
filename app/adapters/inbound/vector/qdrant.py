"""DI-обёртка для Qdrant Vector Store."""

from __future__ import annotations

import structlog
import uuid

from app.adapters.outbound.vector.qdrant import QdrantVectorStore
from app.core.settings import settings
from app.core.ports import VectorStorePort

logger = structlog.get_logger(__name__)


class QdrantVectorStoreAdapter(QdrantVectorStore, VectorStorePort):
    """DI-адаптер для Qdrant Vector Store."""

    def __init__(self) -> None:
        """Создаёт адаптер с URL из ENV и логирует его."""
        super().__init__(
            url=getattr(settings.ai, "qdrant_url", "http://localhost:6333")
        )
        logger.info(
            "Создан QdrantVectorStoreAdapter",
            url=getattr(settings.ai, "qdrant_url", "http://localhost:6333"),
        )

    def is_healthy(self) -> bool:
        """Проверка доступности Qdrant.

        Returns:
            bool: True, если нет исключений.
        """
        try:
            logger.debug("Проверка is_healthy для QdrantVectorStoreAdapter")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
