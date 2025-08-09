"""Секция настроек хранилища файлов."""

from ..base import SettingsBase
from .minio import MinioStorageSettings


class StorageSettings(SettingsBase):
    """Настройки хранилища файлов."""

    minio: MinioStorageSettings = MinioStorageSettings()
