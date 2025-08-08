"""Секция настроек Telegram-бота."""

from pydantic import Field

from ..base import SettingsBase


class TelegramSettings(SettingsBase):
    """Настройки Telegram-бота."""

    telegram_token: str = Field(..., description="Токен Telegram-бота")
    webhook_path: str = Field("", description="Путь для Telegram Webhook")
