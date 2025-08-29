"""Секция настроек OCR-движков."""

from ..base import SettingsBase
from .paddle_en import PaddleEnOCRSettings
from .paddle_ru import PaddleRuOCRSettings


class OCRSettings(SettingsBase):
    """Настройки OCR-движков."""

    paddle_ru: PaddleRuOCRSettings = PaddleRuOCRSettings()
    paddle_en: PaddleEnOCRSettings = PaddleEnOCRSettings()
