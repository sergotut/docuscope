"""DI-адаптер BGE Large.

Подключает модель BGE Large (англоязычная) из Sentence Transformers через DI.
Использует настройки из ENV (settings.ai.bge_large_model).
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.sentence_transformers import (
    SentenceTransformersEmbedding,
)
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class BGELargeEmbeddingAdapter(SentenceTransformersEmbedding):
    """Использует модель BGE Large (англ.).

    Можно задать batch_size. Работает через SentenceTransformersEmbedding.
    """

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""

        config = settings.embed.bge_large

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
            "BGELargeEmbeddingAdapter создан",
            model=config.model_name,
            batch_size=config.batch_size,
            device=self.device,
            quantized=config.quantized,
            space=settings.embed.base.space,
        )
