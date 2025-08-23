"""Пакет documents: публичные реэкспорты."""

from __future__ import annotations

from .document_type_detector import (
    DecisionBasis,
    MagicDetectorTuning,
    MagicDocumentTypeDetector,
)

__all__ = [
    "DecisionBasis",
    "MagicDetectorTuning",
    "MagicDocumentTypeDetector",
 ]