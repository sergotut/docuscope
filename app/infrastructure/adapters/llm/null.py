"""
Null-обёртка для LLM.
"""

import structlog
from app.infrastructure.protocols import LLMPort

logger = structlog.get_logger(__name__)

class NullLLM(LLMPort):
    """Заглушка для LLM."""

    def generate(self, *a, **kw):
        logger.debug("Вызван NullLLM (фолбэк)")
        return "LLM недоступен"

    def is_healthy(self) -> bool:
        return False
