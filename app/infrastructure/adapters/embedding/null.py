"""Null-обёртка для эмбеддера.

Используется как фолбэк, когда нет доступного провайдера эмбеддингов.
"""

import structlog

from app.core.ports import EmbeddingPort

logger = structlog.get_logger(__name__)


class NullEmbedder(EmbeddingPort):
    """Заглушка для эмбеддера.

    Возвращает фиктивные вектора и всегда считается неактивной.
    """

    _dim = 768

    def embed(self, texts):
        """Возвращает нулевые эмбеддинги.

        Args:
            texts (list[str]): Список текстов.

        Returns:
            list[list[float]]: Список векторов из нулей.
        """
        logger.debug("Вызван NullEmbedder (фолбэк)")
        return [[0.0] * self._dim for _ in texts]

    async def embed_async(self, texts, space: str = "semantic"):
        """Асинхронная версия embed (аналогично).

        Args:
            texts (list[str]): Список текстов.
            space (str): Пространство (игнорируется).

        Returns:
            list[list[float]]: Нулевые вектора.
        """
        logger.debug("Вызван async NullEmbedder (фолбэк)")
        return self.embed(texts)

    def is_healthy(self) -> bool:
        """Проверка доступности (всегда False).

        Returns:
            bool: False.
        """
        return False

    def health(self):
        """Подробный отчёт о состоянии (всегда fail).

        Returns:
            dict: Статус, latency, имя модели, размерность.
        """
        return {
            "status": "fail",
            "latency_ms": -1,
            "model": "null",
            "dim": self._dim,
        }
