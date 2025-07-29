"""Прокси-адаптер с резервными эмбеддерами.

Пытается вызвать основной эмбеддер. В случае исключения — переходит к следующему.
Используется для повышения отказоустойчивости при проблемах с сетью или API.
Реализует протокол EmbeddingPort и поддерживает sync/async интерфейсы.
"""

from __future__ import annotations

from typing import List

import structlog

from app.core.ports import EmbeddingPort

logger = structlog.get_logger(__name__)


class FallbackEmbeddingAdapter(EmbeddingPort):
    """Перебирает адаптеры до первого успешного."""

    def __init__(self, *embedders: EmbeddingPort) -> None:
        """Создаёт адаптер с fallback-цепочкой.

        Args:
            *embedders (EmbeddingPort): Один или несколько реализаций EmbeddingPort.

        Raises:
            ValueError: Если список адаптеров пуст.
        """
        if not embedders:
            raise ValueError("Нужен хотя бы один embedder")
        self.embedders: List[EmbeddingPort] = list(embedders)
        logger.info(
            "Создан FallbackEmbeddingAdapter",
            chain=[e.__class__.__name__ for e in self.embedders],
        )

    def embed(self, texts: list[str], space: str = "semantic"):
        """Пытается вызвать 'embed' по цепочке адаптеров.

        Args:
            texts (list[str]): Список строк.
            space (str): Тип пространства (semantic и т.д.).

        Returns:
            list[list[float]]: Вектора эмбеддингов.

        Raises:
            RuntimeError: Если все адаптеры завершились с ошибкой.
        """
        last_exc: Exception | None = None
        for emb in self.embedders:
            try:
                return emb.embed(texts, space)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Embedder failed",
                    embedder=emb.__class__.__name__,
                    error=str(exc),
                )
                last_exc = exc
        raise RuntimeError("Все эмбеддеры упали") from last_exc

    async def embed_async(self, texts: list[str], space: str = "semantic"):
        """Асинхронный fallback по списку адаптеров.

        Args:
            texts (list[str]): Список строк.
            space (str): Пространство эмбеддингов.

        Returns:
            list[list[float]]: Вектора эмбеддингов.

        Raises:
            RuntimeError: Если все адаптеры упали.
        """
        last_exc: Exception | None = None
        for emb in self.embedders:
            try:
                return await emb.embed_async(texts, space)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Async embedder failed",
                    embedder=emb.__class__.__name__,
                    error=str(exc),
                )
                last_exc = exc
        raise RuntimeError("Все эмбеддеры упали") from last_exc

    def is_healthy(self) -> bool:
        """Проверяет, работает ли хотя бы один адаптер.

        Returns:
            bool: True, если есть живой эмбеддер.
        """
        return any(e.is_healthy() for e in self.embedders)

    def health(self):
        """Возвращает health-метрики всех адаптеров.

        Returns:
            dict: Ключи — имена классов, значения — результаты `health()`.
        """
        return {e.__class__.__name__: e.health() for e in self.embedders}
