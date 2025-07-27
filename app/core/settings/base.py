"""Базовый класс для конфигурации приложения.

Используется как родитель для всех секций настроек.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsBase(BaseSettings):
    """Базовый класс для всех секций настроек."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
