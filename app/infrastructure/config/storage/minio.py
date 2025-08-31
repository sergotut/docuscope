"""Секция настроек моделей эмбеддеров."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class MinioStorageSettings(SettingsBase):
    """Базовые настройки MinIO."""

    endpoint: str = Field(
        ..., env="STORAGE_MINIO_ENDPOINT", description="Эндпоинт MinIO."
    )

    access_key: str = Field(
        ...,
        env="STORAGE_MINIO_ACCESS_KEY",
        description="Access key MinIO.",
    )

    secret_key: str = Field(
        ...,
        env="STORAGE_MINIO_SECRET_KEY",
        description="Secret key MinIO.",
    )

    bucket: str = Field(
        ...,
        env="STORAGE_MINIO_BUCKET",
        description="Bucket key MinIO.",
    )
