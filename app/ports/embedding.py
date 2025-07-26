""" Порт для работы с моделями эмбеддингов. """

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """
    Абстракция генерации эмбеддингов.

    Methods:
        embed: Асинхронно генерирует векторные представления для списка текстов.
    """

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Генерирует эмбеддинги для списка строк.

        Args:
            texts (list[str]): Список входных строк.

        Returns:
            list[list[float]]: Список эмбеддингов, соответствующих входным
                строкам.
        """
        raise NotImplementedError
