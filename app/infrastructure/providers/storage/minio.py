"""DI-адаптер MinIO.

Подключает хранилище MinIO через DI.
Использует настройки из конфига.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import MinioStorage
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class MinioStorageAdapter(MinioStorage):
    """Использует MinioStorage."""

    def __init__(self) -> None:
        """Создаёт экземпляр с настройками."""

        config = settings.storage.minio

        super.__init__(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            bucket=config.bucket
        )

        logger.info(
            "MinioStorageAdapter создан",
            endpoint=config.endpoint,
            bucket=config.bucket
        )
