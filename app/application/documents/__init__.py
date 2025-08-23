"""Пакет documents: публичные реэкспорты API уровня приложения.

Экспортируем:
- NormalizedInput, normalize_input, build_probe — нормализация входных данных;
- из .detection: сервис/опции/правила и коды причин/предупреждений.
"""

from __future__ import annotations

from .normalization import (
    NormalizedInput,
    build_probe,
    normalize_input
)

from .detection import (
    ConfidenceRule,
    DecisionRule,
    DetectionDecision,
    DocumentDetectionOptions,
    DocumentDetectionService,
    ForbiddenByDomainRule,
    MimeExtConflictRule,
    ReasonCode,
    REASON_FORBIDDEN_BY_DOMAIN,
    REASON_LOW_CONFIDENCE,
    REASON_MIME_EXT_CONFLICT,
    REASON_UNKNOWN_EXTENSION,
    UnknownExtensionRule,
    WarningCode,
    WARN_INVALID_MIME,
    WARN_MIME_EXT_CONFLICT,
    WARN_UNSAFE_EXTENSION_CHARS,
    WARN_UNKNOWN_EXTENSION,
    is_mime_ext_conflict,
)

__all__ = [
    # Нормализация
    "NormalizedInput",
    "normalize_input",
    "build_probe",
    # Сервис и опции детекции
    "DocumentDetectionService",
    "DetectionDecision",
    "DocumentDetectionOptions",
    # Коды и утилиты
    "ReasonCode",
    "WarningCode",
    "REASON_FORBIDDEN_BY_DOMAIN",
    "REASON_LOW_CONFIDENCE",
    "REASON_MIME_EXT_CONFLICT",
    "REASON_UNKNOWN_EXTENSION",
    "WARN_UNKNOWN_EXTENSION",
    "WARN_INVALID_MIME",
    "WARN_UNSAFE_EXTENSION_CHARS",
    "WARN_MIME_EXT_CONFLICT",
    "is_mime_ext_conflict",
    # Правила
    "DecisionRule",
    "ForbiddenByDomainRule",
    "ConfidenceRule",
    "MimeExtConflictRule",
    "UnknownExtensionRule",
]
