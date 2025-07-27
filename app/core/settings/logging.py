"""
Секция настроек логирования.
"""

from .base import SettingsBase
from pydantic import Field
from typing import Optional

class LoggingSettings(SettingsBase):
    """Настройки логирования."""

    log_level: str = Field("INFO", description="Уровень логирования")
    log_pretty: bool = Field(False, description="Красивый вывод логов")
    log_file: Optional[str] = Field(None, description="Путь к файлу логов (опционально)")
    service_name: str = Field("docuscope", description="Имя сервиса для логирования")
    app_env: str = Field("prod", description="Окружение приложения (prod/dev)")
