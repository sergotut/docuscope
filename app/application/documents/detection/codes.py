"""Коды предупреждений и причин отклонения."""

from __future__ import annotations

from typing import Literal, TypeAlias

__all__ = [
    "ReasonCode",
    "WarningCode",
    "REASON_FORBIDDEN_BY_DOMAIN",
    "REASON_LOW_CONFIDENCE",
    "REASON_MIME_EXT_CONFLICT",
    "REASON_MIME_TYPE_CONFLICT",
    "REASON_UNKNOWN_EXTENSION",
    "WARN_UNKNOWN_EXTENSION",
    "WARN_INVALID_MIME",
    "WARN_UNSAFE_EXTENSION_CHARS",
    "WARN_MIME_EXT_CONFLICT",
    "REASON_MIME_TYPE_CONFLICT",
    "is_mime_ext_conflict",
]

# Причины отклонения.
ReasonCode: TypeAlias = Literal[
    "forbidden_by_domain",
    "low_confidence",
    "mime_extension_conflict",
    "unknown_extension",
]

REASON_FORBIDDEN_BY_DOMAIN: ReasonCode = "forbidden_by_domain"
REASON_LOW_CONFIDENCE: ReasonCode = "low_confidence"
REASON_MIME_EXT_CONFLICT: ReasonCode = "mime_extension_conflict"
REASON_MIME_TYPE_CONFLICT: ReasonCode = "mime_type_conflict"
REASON_UNKNOWN_EXTENSION: ReasonCode = "unknown_extension"

# Предупреждения: строковые коды (часть может иметь детализацию через суффикс).
WarningCode: TypeAlias = str

WARN_UNKNOWN_EXTENSION: WarningCode = "unknown_extension"
WARN_INVALID_MIME: WarningCode = "invalid_mime"
WARN_UNSAFE_EXTENSION_CHARS: WarningCode = "unsafe_extension_chars"
# Детализация допускается: "mime_ext_conflict:<detail>"
WARN_MIME_EXT_CONFLICT: WarningCode = "mime_ext_conflict"


def is_mime_ext_conflict(w: WarningCode) -> bool:
    """Возвращает признак конфликта MIME и расширения.

    Args:
        w (WarningCode): Код предупреждения.

    Returns:
        bool: True, если это конфликт MIME/расширения, иначе False.
    """
    return w == WARN_MIME_EXT_CONFLICT or w.startswith(f"{WARN_MIME_EXT_CONFLICT}:")
