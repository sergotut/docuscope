"""Порт векторного хранилища."""

from __future__ import annotations

from typing import Any, runtime_checkable, Protocol


@runtime_checkable
class VectorStorePort(Protocol):
    """Абстрактный порт векторного хранилища.

    Коллекция создаётся на каждый документ.
    """

    def upsert(
        self,
        doc_id: str,
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """Добавляет или заменяет векторы в коллекции doc_{doc_id}.

        Args:
            doc_id (str): Идентификатор документа.
            vectors (list[list[float]]): Векторы эмбеддингов.
            metadatas (list[dict]): Метаданные для каждой точки.
        """
        ...

    def hybrid_search(
        self,
        doc_id: str,
        query: str,
        top_k: int
    ) -> list[Any]:
        """Гибридный поиск по коллекции doc_{doc_id}.

        Args:
            doc_id (str): ID документа.
            query (str): Поисковый запрос.
            top_k (int): Количество результатов.

        Returns:
            list[dict]: Результаты поиска.
        """
        ...

    def drop(self, doc_id: str) -> None:
        """Удаляет коллекцию, связанную с документом.

        Args:
            doc_id (str): ID документа.
        """
        ...

    def cleanup_expired(self, ttl_hours: int) -> None:
        """Удаляет коллекции, старше указанного TTL.

        Args:
            ttl_hours (int): Сколько часов считаются допустимыми.
        """
        ...

    def is_healthy(self) -> bool:
        """Быстрый health-check.

        Returns:
            bool: True, если хранилище доступно.
        """
        ...
