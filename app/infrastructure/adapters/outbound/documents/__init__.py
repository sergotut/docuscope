"""Пакет documents: публичные реэкспорты."""

from __future__ import annotations

from .document_converter import (
    LibreOfficeConfig,
    LibreOfficeDocumentConverter,
    create_development_converter,
    create_production_converter,
)
from .document_type_detector import (
    DecisionBasis,
    MagicDetectorTuning,
    MagicDocumentTypeDetector,
)

__all__ = [
    "DecisionBasis",
    "MagicDetectorTuning",
    "MagicDocumentTypeDetector",
    "LibreOfficeDocumentConverter",
    "LibreOfficeConfig",
    "create_production_converter",
    "create_development_converter",
]
