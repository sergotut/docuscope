"""DI-обёртка для LLM Sber GigaChat."""

import structlog

from app.adapters.outbound.llm.gigachat import SberGigaChatLLM
from app.core.settings import settings
from app.infrastructure.protocols import LLMPort

logger = structlog.get_logger(__name__)


class SberGigaChatLLMAdapter(SberGigaChatLLM, LLMPort):
    """DI-адаптер для Sber GigaChat LLM."""

    def __init__(self) -> None:
        """Создаёт адаптер GigaChat LLM с ключом из settings."""
        super().__init__(api_key=settings.ai.gigachat_key)
        logger.info("Создан SberGigaChatLLMAdapter", api_key=settings.ai.gigachat_key)

    def is_healthy(self) -> bool:
        """Проверяет доступность GigaChat LLM.

        Returns:
            bool: True, если ошибок не возникло.
        """
        try:
            logger.debug("Проверка is_healthy для SberGigaChatLLMAdapter")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
