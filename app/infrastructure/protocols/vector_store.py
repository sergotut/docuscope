"""Интерфейс (порт) для векторного хранилища.

Реализуется через адаптеры Qdrant и заглушки. Используется в RAG-пайплайне.
"""

from typing import Any, Protocol


class VectorStorePort(Protocol):
    """Абстрактный порт для работы с векторным хранилищем.

    Определяет интерфейс сохранения и поиска по векторным представлениям.
    """

    def upsert(self, vectors: list[list[float]], metadatas: list[dict]) -> None:
        """Сохраняет векторы и их метаданные в хранилище.

        Args:
            vectors (list[list[float]]): Список векторов (обычно эмбеддингов).
            metadatas (list[dict]): Метаданные, соответствующие каждому вектору.
        """
        ...

    def hybrid_search(self, query: str, top_k: int) -> list[Any]:
        """Гибридный поиск по векторной базе.

        Args:
            query (str): Запрос пользователя.
            top_k (int): Количество топ-N результатов.

        Returns:
            list[Any]: Список найденных элементов (обычно словари с payload).
        """
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность хранилища.

        Returns:
            bool: True, если доступно.
        """
        ...
