"""Пакет documents: публичные реэкспорты доменных моделей."""

from __future__ import annotations

from .document import (
    Document,
    DocumentBase,
    DocumentId,
    DocumentMeta,
)
from .chunk import Chunk, ChunkId
from .converters import from_extension, from_mimetype, mime_of
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
from .type_detection import FileProbe, TypeDetectionResult

__all__ = [
    "DocumentId",
    "DocumentBase",
    "Document",
    "DocumentMeta",
    "Chunk",
    "ChunkId",
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
]
