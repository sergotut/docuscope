"""Пакет document_type_detector: публичные реэкспорты."""

from __future__ import annotations

from .magic import MagicDocumentTypeDetector
from .tuning import MagicDetectorTuning
from .types import DecisionBasis

__all__ = [
    "DecisionBasis",
    "MagicDetectorTuning",
    "MagicDocumentTypeDetector",
]
