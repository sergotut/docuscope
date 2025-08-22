"""Пакет детекции документов в application-слое."""

from __future__ import annotations

from .codes import *  # noqa: F401,F403
from .options import DocumentDetectionOptions
from .rules import *  # noqa: F401,F403
from .service import DetectionDecision, DocumentDetectionService

__all__ = [
    "DocumentDetectionService",
    "DetectionDecision",
    "DocumentDetectionOptions",
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
    "DecisionRule",
    "ForbiddenByDomainRule",
    "ConfidenceRule",
    "MimeExtConflictRule",
    "UnknownExtensionRule",
]
