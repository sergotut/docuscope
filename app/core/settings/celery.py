"""
Секция настроек Celery и Redis.
"""

from .base import SettingsBase
from pydantic import Field

class CelerySettings(SettingsBase):
    """Настройки Celery и Redis."""

    redis_host: str = Field("localhost", description="Хост Redis")
    celery_broker_url: str = Field(..., description="URL брокера задач Celery")
    celery_result_backend: str = Field(..., description="Бэкенд хранения результатов Celery")
