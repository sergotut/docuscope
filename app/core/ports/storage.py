"""Порт (интерфейс) для файлового хранилища."""

from __future__ import annotations

from pathlib import Path
from collections.abc import IO
from typing import Protocol, runtime_checkable


@runtime_checkable
class StoragePort(Protocol):
    """Абстрактный порт файлового хранилища.

    Поддерживает загрузку, скачивание, удаление,
    автоматическую очистку по TTL и проверку доступности.
    """

    async def upload(
        self,
        files: list[Path | IO[bytes]],
        *,
        ttl_minutes: int | None = None,
    ) -> list[str]:
        """Загружает файлы в хранилище.

        Args:
            files (list[Path | IO[bytes]]): Пути к файлам или байтовые потоки.
            ttl_minutes (int | None): Время жизни в минутах (опц.).

        Returns:
            list[str]: Список object_name для каждого загруженного файла.
        """
        ...

    async def download(self, object_name: str) -> bytes:
        """Скачивает объект из хранилища.

        Args:
            object_name (str): Уникальное имя объекта.

        Returns:
            bytes: Содержимое файла.
        """
        ...

    async def delete(self, object_name: str) -> None:
        """Удаляет объект немедленно.

        Args:
            object_name (str): Имя удаляемого объекта.
        """
        ...

    async def cleanup_expired(self) -> None:
        """Удаляет все объекты, чей TTL истёк."""
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность хранилища.

        Returns:
            bool: True, если хранилище работает.
        """
        ...
