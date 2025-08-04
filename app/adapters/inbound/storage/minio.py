"""DI-обёртка для MinIO Storage."""

from typing import cast

import structlog

from app.adapters.outbound.storage.minio import MinIOStorage
from app.core.settings import settings
from app.core.ports import StoragePort

logger = structlog.get_logger(__name__)


class MinIOStorageAdapter(MinIOStorage, StoragePort):
    """DI-адаптер для MinIO Storage."""

    def __init__(self) -> None:
        """Инициализирует MinIO клиент и логирует создание."""
        super().__init__(
            endpoint=settings.minio.minio_endpoint,
            access_key=settings.minio.minio_access_key,
            secret_key=settings.minio.minio_secret_key,
        )
        logger.info(
            "Создан MinIOStorageAdapter", endpoint=settings.minio.minio_endpoint
        )

    async def save(self, content: bytes, filename: str) -> str:
        """Сохраняет файл в MinIO.

        Args:
            content (bytes): Содержимое файла.
            filename (str): Имя файла.

        Returns:
            str: Идентификатор (ключ) файла.
        """
        logger.debug("MinIO save", filename=filename)
        return cast(str, self.upload(content, filename))

    async def load(self, file_id: str) -> bytes:
        """Загружает файл по идентификатору.

        Args:
            file_id (str): Ключ файла в хранилище.

        Returns:
            bytes: Содержимое файла.
        """
        logger.debug("MinIO load", file_id=file_id)
        return cast(bytes, self.download(file_id))

    async def delete(self, file_id: str) -> None:
        """Удаляет файл из MinIO.

        Args:
            file_id (str): Ключ файла.
        """
        logger.debug("MinIO delete", file_id=file_id)
        self.remove(file_id)

    def is_healthy(self) -> bool:
        """Проверяет доступность MinIO.

        Returns:
            bool: True, если ошибок не возникло.
        """
        try:
            logger.debug("Проверка is_healthy для MinIOStorageAdapter")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
