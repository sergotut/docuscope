"""DI-обёртка для эмбеддера Sber GigaChat.

Использует settings.ai.gigachat_key и structlog.
"""

import structlog

from app.adapters.outbound.embedding.gigachat import SberGigaChatEmbedding
from app.core.settings import settings
from app.infrastructure.protocols import EmbeddingPort

logger = structlog.get_logger(__name__)


class SberGigaChatEmbeddingAdapter(SberGigaChatEmbedding, EmbeddingPort):
    """DI-адаптер для Sber GigaChat Embedding."""

    def __init__(self) -> None:
        super().__init__(api_key=settings.ai.gigachat_key)
        logger.info(
            "Создан SberGigaChatEmbeddingAdapter", api_key=settings.ai.gigachat_key
        )

    def is_healthy(self) -> bool:
        try:
            logger.debug("Проверка is_healthy для SberGigaChatEmbedding")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
