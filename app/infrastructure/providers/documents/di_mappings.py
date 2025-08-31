"""Маппинги DI для документов.

Содержит словари соответствий ключей настроек и DI-адаптеров
для детекторов и конвертеров документов.
"""

from __future__ import annotations

from .conversion import LibreOfficeDocumentConverterAdapter
from .detection import MagicDocumentTypeDetectorAdapter
from .input_validation import DocumentInputValidationAdapter

__all__ = [
    "DOCUMENT_TYPE_DETECTORS",
    "DOCUMENT_CONVERTERS",
    "DOCUMENT_INPUT_VALIDATORS",
]

# Маппинг детекторов типов документов
DOCUMENT_TYPE_DETECTORS = {
    "magic": MagicDocumentTypeDetectorAdapter,
}

# Маппинг конвертеров документов
DOCUMENT_CONVERTERS = {
    "libreoffice": LibreOfficeDocumentConverterAdapter,
}

# Маппинг валидаторов входных документов
DOCUMENT_INPUT_VALIDATORS = {
    "default": DocumentInputValidationAdapter,
}
