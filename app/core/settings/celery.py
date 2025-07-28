"""Секция настроек Celery и Redis."""

from pydantic import Field

from .base import SettingsBase


class CelerySettings(SettingsBase):
    """Настройки Celery и Redis."""

    redis_host: str = Field("localhost", description="Хост Redis")
    celery_broker_url: str = Field(..., description="URL брокера задач Celery")
    celery_result_backend: str = Field(
        ..., description="Бэкенд хранения результатов Celery"
    )
