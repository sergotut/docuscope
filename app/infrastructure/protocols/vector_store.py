"""Протокол (абстракция) для векторного хранилища (VectorStorePort)."""

from typing import Any, Protocol


class VectorStorePort(Protocol):
    """Абстрактный порт для работы с векторным хранилищем."""

    def upsert(self, vectors: list[list[float]], metadatas: list[dict]) -> None:
        """Сохраняет векторы с метаданными."""
        ...

    def hybrid_search(self, query: str, top_k: int) -> list[Any]:
        """Гибридный поиск по векторной базе."""
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность хранилища."""
        ...
