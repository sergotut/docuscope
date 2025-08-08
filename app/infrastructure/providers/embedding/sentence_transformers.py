"""DI-адаптер произвольной ST-модели из настроек.

Загружает модель из settings.ai.st_model через SentenceTransformersEmbedding.
Подходит для универсальных целей.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import SentenceTransformersEmbedding
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class SentenceTransformersEmbeddingAdapter(SentenceTransformersEmbedding):
    """Использует модель из конфига."""

    def __init__(self) -> None:
        """Создаёт адаптер ST-модели, указанной в конфиге."""

        config = settings.embed.st

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
            "SentenceTransformersEmbeddingAdapter создан",
            model=config.model_name,
            batch_size=config.batch_size,
            device=self.device,
            quantized=config.quantized,
            space=settings.embed.base.space,
        )
