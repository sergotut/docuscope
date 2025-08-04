"""DI-адаптер BGE Large.

Подключает модель BGE Large (русскоязычная) из Sentence Transformers через DI.
Использует настройки из ENV (settings.ai.bge_large_ru_model).
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.sentence_transformers import (
    SentenceTransformersEmbedding,
)
from app.core.settings import settings

logger = structlog.get_logger(__name__)


class BGELargeRuEmbeddingAdapter(SentenceTransformersEmbedding):
    """Использует модель BGE Large (рус.).

    Можно задать batch_size. Работает через SentenceTransformersEmbedding.
    """

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками из settings.ai.bge_large_ru_model."""
        super().__init__(
            model_name=settings.ai.bge_large_ru_model,
            batch_size=64,
            quantized=True,
        )
        logger.info(
            "Создан BGELargeRuEmbeddingAdapter",
            model=settings.ai.bge_large_ru_model,
        )