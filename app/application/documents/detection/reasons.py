"""Коды причин отклонения документов в прикладном слое.

Содержит типы и константы для обозначения причин, по которым
документ может быть отклонён бизнес-правилами системы обработки.
"""

from __future__ import annotations

from typing import Literal, TypeAlias

__all__ = [
    "ReasonCode",
    "REASON_FORBIDDEN_BY_DOMAIN",
    "REASON_LOW_CONFIDENCE",
    "REASON_MIME_EXT_CONFLICT",
    "REASON_MIME_TYPE_CONFLICT",
    "REASON_UNKNOWN_EXTENSION",
]

# Причины отклонения документов бизнес-правилами.
ReasonCode: TypeAlias = Literal[
    "forbidden_by_domain",
    "low_confidence",
    "mime_extension_conflict",
    "mime_type_conflict",
    "unknown_extension",
]

REASON_FORBIDDEN_BY_DOMAIN: ReasonCode = "forbidden_by_domain"
REASON_LOW_CONFIDENCE: ReasonCode = "low_confidence"
REASON_MIME_EXT_CONFLICT: ReasonCode = "mime_extension_conflict"
REASON_MIME_TYPE_CONFLICT: ReasonCode = "mime_type_conflict"
REASON_UNKNOWN_EXTENSION: ReasonCode = "unknown_extension"
