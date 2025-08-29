"""Коды предупреждений для контекста Documents.

Содержит варнинги, специфичные для обработки документов:
нормализации имён файлов, MIME-типов, расширений и детекции типов.
"""

from __future__ import annotations

from app.domain.shared.codes import WarningCode

__all__ = [
    "WARN_UNKNOWN_EXTENSION",
    "WARN_INVALID_MIME",
    "WARN_UNSAFE_EXTENSION_CHARS",
    "WARN_MIME_EXT_CONFLICT",
    "WARN_CONVERSION_QUALITY_LOSS",
    "WARN_CONVERSION_FEATURES_UNSUPPORTED",
    "is_mime_ext_conflict",
]

# Существующие коды, перенесённые из shared
WARN_UNKNOWN_EXTENSION: WarningCode = "unknown_extension"
WARN_INVALID_MIME: WarningCode = "invalid_mime"
WARN_UNSAFE_EXTENSION_CHARS: WarningCode = "unsafe_extension_chars"
WARN_MIME_EXT_CONFLICT: WarningCode = "mime_ext_conflict"

# Коды предупреждений для конвертации документов
WARN_CONVERSION_QUALITY_LOSS: WarningCode = "conversion_quality_loss"
WARN_CONVERSION_FEATURES_UNSUPPORTED: WarningCode = "conversion_features_unsupported"


def is_mime_ext_conflict(w: WarningCode) -> bool:
    """Возвращает признак конфликта MIME и расширения.

    Args:
        w (WarningCode): Код предупреждения.

    Returns:
        bool: True, если это конфликт MIME/расширения, иначе False.
    """
    return w == WARN_MIME_EXT_CONFLICT or w.startswith(f"{WARN_MIME_EXT_CONFLICT}:")
