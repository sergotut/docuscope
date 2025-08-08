"""Секция настроек PostgreSQL."""

from pydantic import Field

from ..base import SettingsBase


class PostgresSettings(SettingsBase):
    """Настройки подключения к PostgreSQL."""

    postgres_dsn: str = Field(..., description="DSN для подключения к PostgreSQL")
