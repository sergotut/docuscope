"""DI-обёртка для эмбеддера YandexGPT.

Использует settings (settings.ai.ygpt_key) и structlog.
"""

import structlog

from app.adapters.outbound.embedding.yagpt import YandexGPTEmbedding
from app.core.settings import settings
from app.infrastructure.protocols import EmbeddingPort

logger = structlog.get_logger(__name__)


class YAGPTEmbeddingAdapter(YandexGPTEmbedding, EmbeddingPort):
    """DI-адаптер для YandexGPT Embedding."""

    def __init__(self) -> None:
        """Создаёт и логгирует адаптер YAGPT Embedding с конфигурацией из settings."""
        super().__init__(key=settings.ai.ygpt_key)
        logger.info("Создан YAGPTEmbeddingAdapter", key=settings.ai.ygpt_key)

    def is_healthy(self) -> bool:
        """Проверяет доступность адаптера.

        Returns:
            bool: True, если ошибок не возникло.
        """
        try:
            logger.debug("Проверка is_healthy для YAGPTEmbedding")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
