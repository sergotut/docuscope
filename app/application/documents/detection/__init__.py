"""Пакет детекции документов в application-слое."""

from __future__ import annotations

from .options import DocumentDetectionOptions
from .reasons import (
    REASON_FORBIDDEN_BY_DOMAIN,
    REASON_LOW_CONFIDENCE,
    REASON_MIME_EXT_CONFLICT,
    REASON_MIME_TYPE_CONFLICT,
    REASON_UNKNOWN_EXTENSION,
    ReasonCode,
)
from .rules import (
    ConfidenceRule,
    DecisionRule,
    ForbiddenByDomainRule,
    MimeExtConflictRule,
    MimeTypeConflictRule,
    UnknownExtensionRule,
)
from .service import DetectionDecision, DocumentDetectionService

__all__ = [
    "DocumentDetectionService",
    "DetectionDecision",
    "DocumentDetectionOptions",
    "ReasonCode",
    "REASON_FORBIDDEN_BY_DOMAIN",
    "REASON_LOW_CONFIDENCE",
    "REASON_MIME_EXT_CONFLICT",
    "REASON_MIME_TYPE_CONFLICT",
    "REASON_UNKNOWN_EXTENSION",
    "DecisionRule",
    "ForbiddenByDomainRule",
    "ConfidenceRule",
    "MimeExtConflictRule",
    "MimeTypeConflictRule",
    "UnknownExtensionRule",
]
