"""Порт (интерфейс) для текстовых эмбеддеров.

Расчёт эмбеддингов, health-check и метрики.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import EmbedderHealthReport
from app.domain.model.retrieval import EmbeddingBatch

__all__ = ["EmbedderPort"]


@runtime_checkable
class EmbedderPort(Protocol):
    """Абстрактный асинхронный порт эмбеддера."""

    async def embed(
        self,
        *,
        texts: list[str],
    ) -> EmbeddingBatch:
        """Вычисляет эмбеддинги для набора строк.

        Args:
            texts (list[str]): Список строк для кодирования.
            space (str): Тип пространства эмбеддингов (например, semantic).

        Returns:
            EmbeddingBatch: Батч эмбеддингов в исходном порядке.
        """
        ...

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если эмбеддер доступен.
        """
        ...

    async def health(self) -> EmbedderHealthReport:
        """Подробный health-репорт.

        Returns:
            EmbedderHealthReport: Метаинформация о состоянии эмбеддера.
        """
        ...

    @property
    def preferred_batch_size(self) -> int:
        """Предпочтительный размер батча.

        Returns:
            int: Количество строк для одного вызова embed.
        """
        ...

    @property
    def embedding_dim(self) -> int:
        """Размерность выходного эмбеддинга.

        Returns:
            int: Количество элементов в одном векторе.
        """
        ...

    @property
    def max_tokens(self) -> int:
        """Максимальное количество токенов на вход.

        Returns:
            int: Ограничение длины входной строки в токенах.
        """
        ...
