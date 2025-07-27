"""
Секция настроек MinIO.
"""

from .base import SettingsBase
from pydantic import Field

class MinioSettings(SettingsBase):
    """Настройки подключения к MinIO."""

    minio_endpoint: str = Field(..., description="Адрес MinIO")
    minio_access_key: str = Field(..., description="Ключ доступа MinIO")
    minio_secret_key: str = Field(..., description="Секретный ключ MinIO")
