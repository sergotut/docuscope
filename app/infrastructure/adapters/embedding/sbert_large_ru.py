"""DI-адаптер SBERT Large RU.

Подключает модель SBERT Large из Sentence Transformers через DI.
Использует настройки из ENV (settings.ai.sbert_large_ru_model).
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.sentence_transformers import (
    SentenceTransformersEmbedding,
)
from app.core.settings import settings

logger = structlog.get_logger(__name__)


class SBERTLargeRuEmbeddingAdapter(SentenceTransformersEmbedding):
    """Использует модель SBERT Large RU.

    Работает через SentenceTransformersEmbedding.
    """

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками из settings.ai.sbert_large_ru_model."""
        super().__init__(model_name=settings.ai.sbert_large_ru_model)
        logger.info(
            "Создан SBERTLargeRuEmbeddingAdapter",
            model=settings.ai.sbert_large_ru_model,
        )