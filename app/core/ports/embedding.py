"""Порт (интерфейс) для текстовых эмбеддеров.

Реализуется адаптерами: BGE Large, GigaChat, SentenceTransformers и др.
Используется в ingest/RAG пайплайнах для кодирования текста в вектора.
"""

from __future__ import annotations

import asyncio
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingPort(Protocol):
    """Абстрактный порт эмбеддера.

    Определяет sync/async интерфейсы и метрики доступности.
    """

    def embed(self, texts: list[str], space: str = "semantic") -> list[list[float]]:
        """Синхронный расчёт эмбеддингов.

        Args:
            texts (list[str]): Список строк для кодирования.
            space (str): Тип пространства (semantic/retrieval и т.д.).

        Returns:
            list[list[float]]: Вектора-эмбеддинги.
        """
        ...

    async def embed_async(
        self, texts: list[str], space: str = "semantic"
    ) -> list[list[float]]:
        """Асинхронный расчёт эмбеддингов (например, через httpx).

        Args:
            texts (list[str]): Входной список строк.
            space (str): Тип embedding-пространства.

        Returns:
            list[list[float]]: Вектора-эмбеддинги.
        """
        ...

    def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если эмбеддер доступен.
        """
        ...

    def health(self) -> dict[str, str | int | float]:
        """Подробный health-репорт.

        Стандартные ключи:
            - status (str): 'ok' | 'fail'
            - latency_ms (float): задержка
            - model (str): название модели
            - dim (int): размерность эмбеддингов

        Returns:
            dict: Отчёт о состоянии эмбеддера.
        """
        ...

    @property
    def preferred_batch_size(self) -> int:
        """Предпочтительный размер батча.

        Returns:
            int: Количество строк для одного вызова метода embed.
        """
        ...

    @property
    def embedding_dim(self) -> int:
        """Размерность выходного эмбеддинга.

        Returns:
            int: Количество флоатов в одном векторе.
        """
        ...

    @property
    def max_tokens(self) -> int:
        """Максимальное количество токенов на вход.

        Returns:
            int: Ограничение входной строки.
        """
        ...