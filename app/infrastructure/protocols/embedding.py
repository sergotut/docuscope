"""Интерфейс (порт) для построения эмбеддингов текста.

Реализуется адаптерами: BGE Large, GigaChat, SentenceTransformers и др.
"""

from typing import List, Protocol


class EmbeddingPort(Protocol):
    """Абстрактный порт эмбеддера.

    Определяет интерфейс для построения эмбеддингов текста и проверки состояния.
    """

    def embed(self, texts: list[str]) -> List[list[float]]:
        """Строит эмбеддинги для переданных текстов.

        Args:
            texts (list[str]): Список входных строк.

        Returns:
            List[list[float]]: Список векторов эмбеддингов.
        """
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность реализации эмбеддера.

        Returns:
            bool: True, если сервис доступен.
        """
        ...
