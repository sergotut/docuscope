"""DI-обёртка для MinIO Storage."""

from typing import cast

import structlog

from app.adapters.outbound.storage.minio import MinIOStorage
from app.core.settings import settings
from app.infrastructure.protocols import StoragePort

logger = structlog.get_logger(__name__)


class MinIOStorageAdapter(MinIOStorage, StoragePort):
    """DI-адаптер для MinIO Storage."""

    def __init__(self) -> None:
        super().__init__(
            endpoint=settings.minio.minio_endpoint,
            access_key=settings.minio.minio_access_key,
            secret_key=settings.minio.minio_secret_key,
        )
        logger.info(
            "Создан MinIOStorageAdapter", endpoint=settings.minio.minio_endpoint
        )

    async def save(self, content: bytes, filename: str) -> str:
        logger.debug("MinIO save", filename=filename)
        return cast(str, self.upload(content, filename))

    async def load(self, file_id: str) -> bytes:
        logger.debug("MinIO load", file_id=file_id)
        return cast(bytes, self.download(file_id))

    async def delete(self, file_id: str) -> None:
        logger.debug("MinIO delete", file_id=file_id)
        self.remove(file_id)

    def is_healthy(self) -> bool:
        try:
            logger.debug("Проверка is_healthy для MinIOStorageAdapter")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
