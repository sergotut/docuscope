"""Пакет libreoffice: LibreOffice адаптер документов.

Содержит высокоуровневую реализацию DocumentConverterPort
на базе LibreOffice с поддержкой process pooling.
"""

from .adapter import LibreOfficeDocumentConverter
from .config import (
    LibreOfficeConfig,
    create_development_converter,
    create_production_converter,
)

__all__ = [
    "LibreOfficeDocumentConverter",
    "LibreOfficeConfig",
    "create_production_converter",
    "create_development_converter",
]
