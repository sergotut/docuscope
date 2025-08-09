"""Сборка конфигурации приложения из секций.

Класс AppSettings агрегирует все секции и предоставляет единый
интерфейс для DI и бизнес-логики.
"""

from .logging import LoggingSettings
from .db import DBSettings
from .telegram import TelegramSettings
from .tokenizer import TokenizerSettings
from .embedding import EmbeddingsSettings
from .storage import StorageSettings


class AppSettings():
    """Финальный класс настроек приложения."""

    logging: LoggingSettings = LoggingSettings()
    db: DBSettings = DBSettings()
    telegram: TelegramSettings = TelegramSettings()
    tokenizer: TokenizerSettings = TokenizerSettings()
    embed: EmbeddingsSettings = EmbeddingsSettings()
    storage: StorageSettings = StorageSettings()
    ocr: OCRSettings = OCRSettings()

settings = AppSettings()
