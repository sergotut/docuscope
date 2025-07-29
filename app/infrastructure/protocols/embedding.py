"""Интерфейс (порт) для построения эмбеддингов текста.

Реализуется адаптерами: BGE Large, GigaChat, SentenceTransformers и др.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Protocol, runtime_checkable


@runtime_checkable
class EmbeddingPort(Protocol):
    """Абстрактный порт эмбеддера.

    Определяет интерфейс для построения эмбеддингов текста (sync/async)
    и получения информации о состоянии модели.
    """

    def embed(self, texts: list[str]) -> List[list[float]]:
        """Строит эмбеддинги для переданных текстов.

        Args:
            texts (list[str]): Список входных строк.

        Returns:
            List[list[float]]: Список векторов эмбеддингов.
        """
        ...

    async def embed_async(
        self,
        texts: list[str],
        space: str = "semantic",
    ) -> List[List[float]]:
        """Строит эмбеддинги асинхронно (например, через httpx.AsyncClient).

        Args:
            texts (list[str]): Список входных строк.
            space (str): Тип пространства (например, 'semantic', 'retrieval').

        Returns:
            List[List[float]]: Эмбеддинги для всех текстов.
        """
        ...

    def is_healthy(self) -> bool:
        """Короткая проверка доступности.

        Returns:
            bool: True, если сервис доступен.
        """
        ...

    def health(self) -> Dict[str, str | int | float]:
        """Подробный отчёт о состоянии адаптера.

        Стандартные ключи:
            status (str): `"ok"` | `"fail"`
            latency_ms (float): время отклика
            model (str): название или версия модели
            dim (int): размерность эмбеддингов

        Returns:
            Dict[str, str | int | float]: Метрики и статус работы модели.
        """
        ...
