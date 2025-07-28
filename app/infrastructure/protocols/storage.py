"""Интерфейс (порт) для хранилища файлов.

Реализуется через MinIO, заглушки.
"""

from typing import Protocol


class StoragePort(Protocol):
    """Абстрактный порт хранилища файлов.

    Определяет асинхронный интерфейс для операций над файлами и проверки состояния.
    """

    async def save(self, content: bytes, filename: str) -> str:
        """Сохраняет файл в хранилище.

        Args:
            content (bytes): Содержимое файла.
            filename (str): Имя файла.

        Returns:
            str: Идентификатор сохранённого файла.
        """
        ...

    async def load(self, file_id: str) -> bytes:
        """Загружает файл по идентификатору.

        Args:
            file_id (str): Идентификатор (ключ) файла.

        Returns:
            bytes: Содержимое файла.
        """
        ...

    async def delete(self, file_id: str) -> None:
        """Удаляет файл из хранилища.

        Args:
            file_id (str): Идентификатор файла.
        """
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность хранилища.

        Returns:
            bool: True, если хранилище доступно.
        """
        ...
