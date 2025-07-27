"""
Секция настроек PostgreSQL.
"""

from .base import SettingsBase
from pydantic import Field

class PostgresSettings(SettingsBase):
    """Настройки подключения к PostgreSQL."""

    postgres_dsn: str = Field(..., description="DSN для подключения к PostgreSQL")
