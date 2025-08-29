"""Пакет documents: публичные реэкспорты API уровня приложения.

Экспортируем:
- NormalizedInput, normalize_input, build_probe — нормализация входных данных;
- из .detection: сервис/опции/правила и коды причин (application-слой).
"""

from __future__ import annotations

from .conversion import DocumentConversionService
from .detection import (
    REASON_FORBIDDEN_BY_DOMAIN,
    REASON_LOW_CONFIDENCE,
    REASON_MIME_EXT_CONFLICT,
    REASON_UNKNOWN_EXTENSION,
    ConfidenceRule,
    DecisionRule,
    DetectionDecision,
    DocumentDetectionOptions,
    DocumentDetectionService,
    ForbiddenByDomainRule,
    MimeExtConflictRule,
    ReasonCode,
    UnknownExtensionRule,
)
from .normalization import NormalizedInput, build_probe, normalize_input

__all__ = [
    # Нормализация
    "NormalizedInput",
    "normalize_input",
    "build_probe",
    # Сервис и опции детекции
    "DocumentDetectionService",
    "DetectionDecision",
    "DocumentDetectionOptions",
    # Коды причин (application-слой)
    "ReasonCode",
    "REASON_FORBIDDEN_BY_DOMAIN",
    "REASON_LOW_CONFIDENCE",
    "REASON_MIME_EXT_CONFLICT",
    "REASON_UNKNOWN_EXTENSION",
    # Правила
    "DecisionRule",
    "ForbiddenByDomainRule",
    "ConfidenceRule",
    "MimeExtConflictRule",
    "UnknownExtensionRule",
    # Конвертация документов
    "DocumentConversionService",
]
