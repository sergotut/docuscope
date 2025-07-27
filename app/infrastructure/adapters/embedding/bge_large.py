"""
DI-обёртка для эмбеддера BGE Large.

Использует settings.ai.bge_large_model и structlog.
"""

import structlog
from app.adapters.outbound.embedding.bge_large import BGELargeEmbedding
from app.core.settings import settings
from app.infrastructure.protocols import EmbeddingPort

logger = structlog.get_logger(__name__)

class BGELargeEmbeddingAdapter(BGELargeEmbedding, EmbeddingPort):
    """DI-адаптер для BGE Large Embedding."""

    def __init__(self) -> None:
        super().__init__(model_name=settings.ai.bge_large_model)
        logger.info(
            "Создан BGELargeEmbeddingAdapter",
            model=settings.ai.bge_large_model
        )

    def is_healthy(self) -> bool:
        try:
            logger.debug("Проверка is_healthy для BGELargeEmbedding")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
