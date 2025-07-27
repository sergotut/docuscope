"""Сборка конфигурации приложения из секций.

Класс AppSettings агрегирует все секции и предоставляет единый интерфейс для DI и бизнес-логики.
"""

from .ai import AISettings
from .celery import CelerySettings
from .logging import LoggingSettings
from .minio import MinioSettings
from .postgres import PostgresSettings
from .telegram import TelegramSettings


class AppSettings(
    PostgresSettings,
    MinioSettings,
    AISettings,
    TelegramSettings,
    CelerySettings,
    LoggingSettings,
):
    """Финальный класс настроек приложения.
    Все поля из секций доступны как свойства экземпляра.
    """

    pass


settings = AppSettings()
