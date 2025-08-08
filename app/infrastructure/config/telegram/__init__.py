"""Секция настроек Телеграм."""

from ..base import SettingsBase
from .telegram_settings import TelegramSettings


class TelegramSettings(SettingsBase):
    """Настройки Телеграм."""

    base: TelegramSettings = TelegramSettings()