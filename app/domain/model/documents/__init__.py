"""Пакет documents: публичные реэкспорты доменных моделей."""

from __future__ import annotations

from .chunk import Chunk, ChunkId, check_chunk_id, to_chunk_id
from .conversion import (
    SUPPORTED_CONVERSIONS,
    ConversionRequest,
    ConversionResult,
    ConversionStatus,
    is_conversion_supported,
)
from .converters import from_extension, from_mimetype, mime_of
from .document import (
    Document,
    DocumentBase,
    DocumentId,
    DocumentMeta,
    check_document_id,
    to_document_id,
    check_original_name,
    to_original_name,
)
from .type_detection import FileProbe, TypeDetectionResult
from .types import (
    ALLOWED_DOCUMENT_TYPES,
    DOCUMENT_FAMILY_BY_TYPE,
    DocumentFamily,
    DocumentType,
    Permission,
    family_of,
    is_allowed_type,
    permission_of,
)
from .warnings import (
    WARN_CONVERSION_FEATURES_UNSUPPORTED,
    WARN_CONVERSION_QUALITY_LOSS,
    WARN_INVALID_MIME,
    WARN_MIME_EXT_CONFLICT,
    WARN_UNKNOWN_EXTENSION,
    WARN_UNSAFE_EXTENSION_CHARS,
    is_mime_ext_conflict,
)

__all__ = [
    # Документы
    "DocumentId",
    "DocumentBase",
    "Document",
    "DocumentMeta",
    "check_document_id",
    "check_original_name",
    "to_document_id",
    "to_original_name",
    # Фрагменты документов
    "Chunk",
    "ChunkId",
    "to_chunk_id",
    "check_chunk_id",
    "DocumentFamily",
    "DocumentType",
    "Permission",
    "DOCUMENT_FAMILY_BY_TYPE",
    "ALLOWED_DOCUMENT_TYPES",
    "family_of",
    "is_allowed_type",
    "permission_of",
    "from_extension",
    "from_mimetype",
    "mime_of",
    "FileProbe",
    "TypeDetectionResult",
    # Варнинги контекста Documents
    "WARN_INVALID_MIME",
    "WARN_MIME_EXT_CONFLICT",
    "WARN_UNSAFE_EXTENSION_CHARS",
    "WARN_UNKNOWN_EXTENSION",
    "WARN_CONVERSION_QUALITY_LOSS",
    "WARN_CONVERSION_FEATURES_UNSUPPORTED",
    "is_mime_ext_conflict",
    # Модели конвертации документов
    "ConversionRequest",
    "ConversionResult",
    "ConversionStatus",
    "SUPPORTED_CONVERSIONS",
    "is_conversion_supported",
]
