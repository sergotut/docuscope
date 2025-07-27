"""
Сборка конфигурации приложения из секций.

Класс AppSettings агрегирует все секции и предоставляет единый интерфейс для DI и бизнес-логики.
"""

from .postgres import PostgresSettings
from .minio import MinioSettings
from .ai import AISettings
from .telegram import TelegramSettings
from .celery import CelerySettings
from .logging import LoggingSettings

class AppSettings(
    PostgresSettings,
    MinioSettings,
    AISettings,
    TelegramSettings,
    CelerySettings,
    LoggingSettings,
):
    """
    Финальный класс настроек приложения.
    Все поля из секций доступны как свойства экземпляра.
    """
    pass

settings = AppSettings()
