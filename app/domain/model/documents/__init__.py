"""Пакет documents: публичные реэкспорты доменных моделей."""

from .document import (
    DocumentId,
    DocumentBase,
    Document,
    DocumentMeta
)
from .chunk import Chunk, ChunkId
from .types import (
    DocumentFamily,
    DocumentType,
    Permission,
    DOCUMENT_FAMILY_BY_TYPE,
    ALLOWED_DOCUMENT_TYPES,
    family_of,
    is_allowed_type,
    permission_of,
)
from .converters import from_extension, from_mimetype
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
    "FileProbe",
    "TypeDetectionResult",
]
