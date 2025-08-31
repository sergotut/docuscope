"""Пакет documents: публичные реэкспорты портов обработки документов."""

from __future__ import annotations

from .document_converter import DocumentConverterPort
from .document_type_detector import DocumentTypeDetectorPort

__all__ = [
    "DocumentConverterPort",
    "DocumentTypeDetectorPort",
]
