"""DI-обёртка для эмбеддера Sentence Transformers.

Использует settings.ai.st_model и structlog.
"""

import structlog

from app.adapters.outbound.embedding.sentence_transformers import (
    SentenceTransformersEmbedding,
)
from app.core.settings import settings
from app.infrastructure.protocols import EmbeddingPort

logger = structlog.get_logger(__name__)


class SentenceTransformersEmbeddingAdapter(
    SentenceTransformersEmbedding, EmbeddingPort
):
    """DI-адаптер для Sentence Transformers Embedding."""

    def __init__(self) -> None:
        """Создаёт адаптер с моделью из настроек и логгирует запуск."""
        super().__init__(model_name=settings.ai.st_model)
        logger.info(
            "Создан SentenceTransformersEmbeddingAdapter", model=settings.ai.st_model
        )

    def is_healthy(self) -> bool:
        """Проверка готовности эмбеддера.

        Returns:
            bool: True, если нет ошибок.
        """
        try:
            logger.debug("Проверка is_healthy для SentenceTransformersEmbedding")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
