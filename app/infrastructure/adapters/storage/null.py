"""Null-обёртка для хранилища файлов."""

import structlog

from app.infrastructure.protocols import StoragePort

logger = structlog.get_logger(__name__)


class NullStorage(StoragePort):
    """Заглушка для хранилища."""

    async def save(self, content, filename):
        logger.debug("Вызван NullStorage (фолбэк)", filename=filename)
        raise RuntimeError("Storage недоступен")

    async def load(self, file_id):
        logger.debug("Вызван NullStorage (фолбэк)", file_id=file_id)
        raise RuntimeError("Storage недоступен")

    async def delete(self, file_id):
        logger.debug("Вызван NullStorage (фолбэк)", file_id=file_id)
        pass

    def is_healthy(self) -> bool:
        return False
