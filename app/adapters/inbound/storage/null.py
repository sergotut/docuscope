"""Null-обёртка для хранилища файлов."""

import structlog

from app.core.ports import StoragePort

logger = structlog.get_logger(__name__)


class NullStorage(StoragePort):
    """Заглушка для хранилища."""

    async def save(self, content, filename):
        """Вызывает исключение при попытке сохранить файл.

        Args:
            content: Содержимое файла.
            filename: Имя файла.

        Raises:
            RuntimeError: Storage недоступен.
        """
        logger.debug("Вызван NullStorage (фолбэк)", filename=filename)
        raise RuntimeError("Storage недоступен")

    async def load(self, file_id):
        """Вызывает исключение при попытке загрузки файла.

        Args:
            file_id: Идентификатор файла.

        Raises:
            RuntimeError: Storage недоступен.
        """
        logger.debug("Вызван NullStorage (фолбэк)", file_id=file_id)
        raise RuntimeError("Storage недоступен")

    async def delete(self, file_id):
        """Пытается удалить файл (ничего не делает).

        Args:
            file_id: Идентификатор файла.
        """
        logger.debug("Вызван NullStorage (фолбэк)", file_id=file_id)
        pass

    def is_healthy(self) -> bool:
        """Всегда возвращает False.

        Returns:
            bool: False
        """
        return False
