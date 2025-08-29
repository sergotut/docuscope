"""Порт (интерфейс) для файлового хранилища.

Реализации могут возбуждать StorageError.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.collections import CollectionName
from app.domain.model.shared import Blob, ObjectName, StoredObject, UploadBatch

__all__ = ["StoragePort"]


@runtime_checkable
class StoragePort(Protocol):
    """Абстрактный асинхронный порт файлового хранилища."""

    async def upload(
        self,
        blobs: list[Blob],
        *,
        ttl_minutes: int | None = None,
    ) -> UploadBatch:
        """Загружает объекты в хранилище.

        Args:
            blobs (list[Blob]): Двоичные данные объектов.
            ttl_minutes (int | None): Время жизни объектов в минутах. Если
                None, объекты бессрочные.

        Returns:
            UploadBatch: Результат пакетной загрузки с именами и сроками жизни.
        """
        ...

    async def upload_to_collection(
        self,
        collection: CollectionName,
        blobs: list[Blob],
        *,
        ttl_minutes: int | None = None,
    ) -> UploadBatch:
        """Загружает объекты в «папку» коллекции.

        Ключи в сторе получают префикс <collection>/....

        Args:
            collection (CollectionName): Имя коллекции для префикса.
            blobs (list[Blob]): Двоичные данные объектов.
            ttl_minutes (int | None): Время жизни объектов в минутах. Если
                None, объекты бессрочные.

        Returns:
            UploadBatch: Результат пакетной загрузки с именами и сроками жизни.
        """
        ...

    async def download(self, object_name: ObjectName) -> Blob:
        """Скачивает объект из хранилища.

        Args:
            object_name (ObjectName): Уникальное имя объекта.

        Returns:
            Blob: Содержимое и MIME-тип, если известен.
        """
        ...

    async def stat(self, object_name: ObjectName) -> StoredObject:
        """Возвращает метаданные объекта.

        Args:
            object_name (ObjectName): Имя объекта в хранилище.

        Returns:
            StoredObject: Имя и момент истечения, если задан.
        """
        ...

    async def delete(self, object_name: ObjectName) -> None:
        """Удаляет объект немедленно.

        Args:
            object_name (ObjectName): Имя удаляемого объекта.
        """
        ...

    async def delete_collection(self, collection: CollectionName) -> None:
        """Удаляет все объекты коллекции (по префиксу).

        Args:
            collection (CollectionName): Имя коллекции (префикс).
        """
        ...

    async def cleanup_expired(self) -> None:
        """Удаляет все объекты, чей TTL истёк."""
        ...

    async def is_healthy(self) -> bool:
        """Проверяет доступность хранилища.

        Returns:
            bool: True, если хранилище доступно и готово к работе.
        """
        ...
