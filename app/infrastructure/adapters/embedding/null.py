"""Null-обёртка для эмбеддера."""

import structlog

from app.infrastructure.protocols import EmbeddingPort

logger = structlog.get_logger(__name__)


class NullEmbedder(EmbeddingPort):
    """Заглушка для эмбеддера."""

    def embed(self, texts):
        """Возвращает нулевые эмбеддинги.

        Args:
            texts (list[str]): Список текстов.

        Returns:
            list[list[float]]: Список векторов из нулей.
        """
        logger.debug("Вызван NullEmbedder (фолбэк)")
        return [[0.0] * 768 for _ in texts]

    def is_healthy(self) -> bool:
        """Проверка состояния (всегда False).

        Returns:
            bool: False.
        """
        return False
