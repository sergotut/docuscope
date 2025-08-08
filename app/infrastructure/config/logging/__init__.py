"""Секция настроек эмбеддеров."""

from ..base import SettingsBase
from .looging_settings import LoggingSettings


class LoggingSettings(SettingsBase):
    """Настройки логирования."""

    base: LoggingSettings = LoggingSettings()