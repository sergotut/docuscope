"""DI-адаптер Yandex GPT.

Подключает облачный эмбеддинг-эндпоинт Yandex GPT через API-ключ из настроек.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.yagpt import YAGPTEmbedding
from app.core.settings import settings

logger = structlog.get_logger(__name__)


class YAGPTEmbeddingAdapter(YAGPTEmbedding):
    """Использует облачный эндпоинт Yandex GPT."""

    def __init__(self) -> None:
        """Создаёт адаптер с API-ключом из settings.ai.ygpt_key."""
        super().__init__(api_key=settings.ai.ygpt_key)
        logger.info("Создан YAGPTEmbeddingAdapter")
