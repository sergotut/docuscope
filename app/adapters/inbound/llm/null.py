"""Null-обёртка для LLM."""

import structlog

from app.core.ports import LLMPort

logger = structlog.get_logger(__name__)


class NullLLM(LLMPort):
    """Заглушка для LLM.

    Используется при отключённой или неинициализированной модели.
    """

    def generate(self, *a, **kw):
        """Возвращает заглушку-ответ при генерации текста.

        Args:
            *a: Позиционные аргументы (игнорируются).
            **kw: Именованные аргументы (игнорируются).

        Returns:
            str: Сообщение о недоступности LLM.
        """
        logger.debug("Вызван NullLLM (фолбэк)")
        return "LLM недоступен"

    def is_healthy(self) -> bool:
        """Всегда возвращает False.

        Returns:
            bool: False
        """
        return False
