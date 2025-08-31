"""Сборка конфигурации приложения из секций.

Класс AppSettings агрегирует все секции и предоставляет единый
интерфейс для DI и бизнес-логики.
"""

from .db import DBSettings
from .documents import DocumentsSettings
from .embedding import EmbeddingsSettings
from .logging import LoggingSettings
from .ocr import OCRSettings
from .storage import StorageSettings
from .telegram import TelegramSettings
from .tokenizer import TokenizerSettings


class AppSettings:
    """Финальный класс настроек приложения."""

    logging: LoggingSettings = LoggingSettings()
    db: DBSettings = DBSettings()
    telegram: TelegramSettings = TelegramSettings()
    tokenizer: TokenizerSettings = TokenizerSettings()
    embed: EmbeddingsSettings = EmbeddingsSettings()
    storage: StorageSettings = StorageSettings()
    ocr: OCRSettings = OCRSettings()
    documents: DocumentsSettings = DocumentsSettings()


settings = AppSettings()
