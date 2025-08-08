"""DI-адаптер SBERT Large RU.

Подключает модель SBERT Large из Sentence Transformers через DI.
Использует настройки из ENV (settings.ai.sbert_large_ru_model).
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.sentence_transformers import (
    SentenceTransformersEmbedding,
)
from ..config import settings

logger = structlog.get_logger(__name__)


class SBERTLargeRuEmbeddingAdapter(SentenceTransformersEmbedding):
    """Использует модель SBERT Large RU.

    Работает через SentenceTransformersEmbedding.
    """

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""

        config = settings.embed.sbert_large_ru

        super().__init__(
            model_name=config.model_name,
            device=config.device,
            batch_size=config.batch_size,
            space=settings.embed.base.space,
            dtype=config.dtype,
            quantized=config.quantized,
            max_tokens=config.max_tokens
        )

        logger.info(
            "SBERTLargeRuEmbeddingAdapter создан",
            model=config.model_name,
            batch_size=config.batch_size,
            device=self.device,
            quantized=config.quantized,
            space=settings.embed.base.space,
        )