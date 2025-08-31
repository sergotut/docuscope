"""Настройки для работы с документами.

Агрегирует общие настройки и настройки детекции и конвертации документов.
"""

from __future__ import annotations

from .common import CommonDocumentSettings
from .conversion import LibreOfficeConverterSettings
from .detection import MagicDetectorSettings

__all__ = [
    "CommonDocumentSettings",
    "MagicDetectorSettings",
    "LibreOfficeConverterSettings",
    "DocumentsSettings",
]


class DocumentsSettings:
    """Агрегированные настройки для работы с документами.

    Attributes:
        common: Общие настройки для всех операций с документами.
        detection: Настройки детекции типов документов.
        conversion: Настройки конвертации документов.
    """

    def __init__(self) -> None:
        """Инициализирует настройки документов."""
        self.common = CommonDocumentSettings()
        self.detection = MagicDetectorSettings()
        self.conversion = LibreOfficeConverterSettings()
