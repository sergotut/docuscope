"""Секция настроек OCR-движков."""

from ..base import SettingsBase
from .paddle_ru import PaddleRuOCRSettings
from .paddle_en import PaddleEnOCRSettings


class OCRSettings(SettingsBase):
    """Настройки OCR-движков."""

    paddle_ru: PaddleRuOCRSettings = PaddleRuOCRSettings()
    paddle_en: PaddleEnOCRSettings = PaddleEnOCRSettings()
