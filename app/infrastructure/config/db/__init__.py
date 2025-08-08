"""Секция настроек базы данных."""

from ..base import SettingsBase
from .postgres_settings import PostgresSettings


class DBSettings(SettingsBase):
    """Настройки базы данных."""

    postgres: PostgresSettings = PostgresSettings()
    