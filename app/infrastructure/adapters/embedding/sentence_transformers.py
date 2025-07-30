"""DI-адаптер произвольной ST-модели из настроек.

Загружает модель из settings.ai.st_model через SentenceTransformersEmbedding.
Подходит для универсальных целей.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.sentence_transformers import (
    SentenceTransformersEmbedding,
)
from app.core.settings import settings

logger = structlog.get_logger(__name__)


class SentenceTransformersEmbeddingAdapter(SentenceTransformersEmbedding):
    """Использует модель из settings.ai.st_model."""

    def __init__(self) -> None:
        """Создаёт адаптер ST-модели, указанной в settings.ai.st_model."""
        super().__init__(model_name=settings.ai.st_model)
        logger.info(
            "Создан SentenceTransformersEmbeddingAdapter",
            model=settings.ai.st_model,
        )
