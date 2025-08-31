"""DI-адаптер Yandex GPT.

Подключает облачный эмбеддинг-эндпоинт Yandex GPT через API-ключ из настроек.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import YAGPTEmbedder
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class YAGPTEmbeddingAdapter(YAGPTEmbedder):
    """Использует облачный эндпоинт Yandex GPT."""

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""
        config = settings.embed.yagpt

        super().__init__(
            api_key=config.api_key,
            model_name=config.model_name,
            endpoint=config.endpoint,
            timeout=settings.embed.base.timeout,
            batch_size=config.batch_size,
        )

        logger.info(
            "YAGPTEmbeddingAdapter создан",
            model=config.model_name,
            endpoint=config.endpoint,
            batch_size=config.batch_size,
        )
