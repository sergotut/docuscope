""" Порт для векторных БД / поисковых движков. """

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class VectorStorePort(ABC):
    """
    Абстракция для upsert-операций и гибридного поиска.

    Methods:
        upsert: Сохраняет эмбеддинги вместе с метаданными.
        hybrid_search: Выполняет гибридный поиск по запросу.
    """

    @abstractmethod
    async def upsert(
        self,
        vectors: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """
        Сохраняет эмбеддинги вместе с метаданными.

        Args:
            vectors (list[list[float]]): Векторы документов.
            metadatas (list[dict[str, Any]]): Связанные метаданные.
        """
        raise NotImplementedError

    @abstractmethod
    async def hybrid_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """
        Возвращает топ-k релевантных документов.

        Args:
            query (str): Текстовый поисковый запрос.
            top_k (int): Количество результатов.

        Returns:
            list[dict[str, Any]]: Список метаданных найденных документов.
        """
        raise NotImplementedError
