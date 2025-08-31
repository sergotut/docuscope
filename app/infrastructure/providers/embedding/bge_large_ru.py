"""DI-адаптер BGE Large Ru.

Подключает модель BGE Large (русскоязычная) из Sentence Transformers через DI.
Использует настройки из конфига.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import SentenceTransformersEmbedder
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class BGELargeRuEmbeddingAdapter(SentenceTransformersEmbedder):
    """Использует модель BGE Large (рус.).

    Можно задать batch_size. Работает через SentenceTransformersEmbedding.
    """

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""
        config = settings.embed.bge_large

        super().__init__(
            model_name=config.model_name,
            device=config.device,
            batch_size=config.batch_size,
            dtype=config.dtype,
            quantized=config.quantized,
            max_tokens=config.max_tokens,
        )

        logger.info(
            "BGELargeRuEmbeddingAdapter создан",
            model=config.model_name,
            batch_size=config.batch_size,
            device=self.device,
            quantized=config.quantized,
        )
