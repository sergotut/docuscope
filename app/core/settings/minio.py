"""Секция настроек MinIO."""

from pydantic import Field

from .base import SettingsBase


class MinioSettings(SettingsBase):
    """Настройки подключения к MinIO."""

    minio_endpoint: str = Field(..., description="Адрес MinIO")
    minio_access_key: str = Field(..., description="Ключ доступа MinIO")
    minio_secret_key: str = Field(..., description="Секретный ключ MinIO")
