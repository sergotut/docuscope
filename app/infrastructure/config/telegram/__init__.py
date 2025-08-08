"""Секция настроек Телеграм"""

from ..base import SettingsBase
from .postgres_settings import PostgresSettings


class TelegramSettings(SettingsBase):
    """Настройки Телеграм"""

    base: TelegramSettings = TelegramSettings()