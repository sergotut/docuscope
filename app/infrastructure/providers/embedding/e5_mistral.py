"""DI-адаптер E5-Mistral.

Подключает локальный REST-эндпоинт llama.cpp, реализующий модель E5-Mistral.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import E5MistralEmbedding
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class E5MistralEmbeddingAdapter(E5MistralEmbedding):
    """Использует локальный llama.cpp-эндпоинт."""

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""
        config = settings.embed.e5_mistral

        super().__init__(
            host=config.host,
            port=config.port,
            model_name=config.model_name,
            batch_size=config.batch_size,
            space=settings.embed.base.space,
            dim=config.dim,
        )

        logger.info(
            "E5MistralEmbeddingAdapter создан",
            model=config.model_name,
            batch_size=config.batch_size,
            space=settings.embed.base.space,
        )
