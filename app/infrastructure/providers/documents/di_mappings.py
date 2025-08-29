"""Маппинги DI для документов.

Содержит словари соответствий ключей настроек и DI-адаптеров
для детекторов и конвертеров документов.
"""

from __future__ import annotations

from .conversion import LibreOfficeDocumentConverterAdapter
from .detection import MagicDocumentTypeDetectorAdapter

__all__ = [
    "DOCUMENT_TYPE_DETECTORS",
    "DOCUMENT_CONVERTERS",
]

# Маппинг детекторов типов документов
DOCUMENT_TYPE_DETECTORS = {
    "magic": MagicDocumentTypeDetectorAdapter,
}

# Маппинг конвертеров документов
DOCUMENT_CONVERTERS = {
    "libreoffice": LibreOfficeDocumentConverterAdapter,
}
