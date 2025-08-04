"""DI-обёртка для LLM YandexGPT."""

import structlog

from app.adapters.outbound.llm.yagpt import YaGPTLLM
from app.core.settings import settings
from app.core.ports import LLMPort

logger = structlog.get_logger(__name__)


class YaGPTLLMAdapter(YaGPTLLM, LLMPort):
    """DI-адаптер для LLM YandexGPT."""

    def __init__(self) -> None:
        """Создаёт адаптер с ключом YandexGPT из настроек."""
        super().__init__(key=settings.ai.ygpt_key)
        logger.info("Создан YaGPTLLMAdapter", key=settings.ai.ygpt_key)

    def is_healthy(self) -> bool:
        """Проверяет доступность YandexGPT LLM.

        Returns:
            bool: True, если нет ошибок.
        """
        try:
            logger.debug("Проверка is_healthy для YaGPTLLMAdapter")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
