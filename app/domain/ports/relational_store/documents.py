"""Порт (интерфейс) репозитория метаданных документов.

Определяет минимальный интерфейс для сохранения и выборки метаданных документов
по коллекциям, а также их каскадного удаления.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.collections import CollectionName
from app.domain.model.documents import DocumentMeta

__all__ = ["DocumentMetaRepositoryPort"]


@runtime_checkable
class DocumentMetaRepositoryPort(Protocol):
    """Репозиторий метаданных документов."""

    async def add(self, meta: DocumentMeta) -> None:
        """Сохраняет метаданные документа.

        Args:
            meta (DocumentMeta): Метаданные документа без контента.
        """

    async def list_by_collection(self, name: CollectionName) -> list[DocumentMeta]:
        """Возвращает все документы коллекции.

        Args:
            name (CollectionName): Имя коллекции.

        Returns:
            list[DocumentMeta]: Список метаданных документов.
        """

    async def delete_by_collection(self, name: CollectionName) -> None:
        """Удаляет все документы коллекции.

        Args:
            name (CollectionName): Имя коллекции.
        """
