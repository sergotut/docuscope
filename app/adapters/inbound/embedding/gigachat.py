"""DI-адаптер Sber GigaChat.

Подключает облачный эмбеддинг-эндпоинт GigaChat через OAuth-токен из настроек.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.gigachat import SberGigaChatEmbedding
from app.core.settings import settings

logger = structlog.get_logger(__name__)


class SberGigaChatEmbeddingAdapter(SberGigaChatEmbedding):
    """Использует REST-эндпоинт GigaChat."""

    def __init__(self) -> None:
        """Создаёт адаптер с токеном из settings.ai.gigachat_key."""
        super().__init__(api_key=settings.ai.gigachat_key)
        logger.info("Создан SberGigaChatEmbeddingAdapter")
