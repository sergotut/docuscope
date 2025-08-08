"""DI-адаптер Sber GigaChat.

Подключает облачный эмбеддинг-эндпоинт GigaChat через OAuth-токен из настроек.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.gigachat import SberGigaChatEmbedding
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class SberGigaChatEmbeddingAdapter(SberGigaChatEmbedding):
    """Использует REST-эндпоинт GigaChat."""

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""

        config = settings.embed.gigachat

        super().__init__(
            api_key=config.api_key,
            model_name=config.model_name,
            endpoint=config.endpoint,
            timeout=settings.embed.base.timeout,
            batch_size=config.batch_size,
            space=settings.embed.base.space
        )

        logger.info(
            "SberGigaChatEmbeddingAdapter создан",
            model=config.model_name,
            batch_size=config.batch_size,
            space=settings.embed.base.space,
        )
