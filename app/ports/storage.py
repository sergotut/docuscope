"""Порт для внешнего хранения файлов."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class StoragePort(ABC):
    """Абстракция хранилища документов.

    Methods:
        save: Сохраняет файл и возвращает его ID.
        load: Загружает содержимое файла по ID.
        delete: Удаляет файл.
    """

    @abstractmethod
    async def save(self, file_path: Path, content: bytes) -> str:
        """Сохраняет файл.

        Args:
            file_path (Path): Местоположение оригинального файла.
            content (bytes): Содержимое файла.

        Returns:
            str: Уникальный идентификатор сохранённого файла.
        """
        raise NotImplementedError

    @abstractmethod
    async def load(self, file_id: str) -> bytes:
        """Возвращает содержимое файла по ID.

        Args:
            file_id (str): Уникальный идентификатор файла.

        Returns:
            bytes: Содержимое файла.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, file_id: str) -> None:
        """Удаляет файл.

        Args:
            file_id (str): Уникальный идентификатор файла.
        """
        raise NotImplementedError
