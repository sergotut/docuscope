"""
Секция настроек Telegram-бота.
"""

from .base import SettingsBase
from pydantic import Field

class TelegramSettings(SettingsBase):
    """Настройки Telegram-бота."""

    telegram_token: str = Field(..., description="Токен Telegram-бота")
    webhook_path: str = Field("", description="Путь для Telegram Webhook")
