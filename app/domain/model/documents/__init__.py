"""Пакет documents: публичные реэкспорты доменных моделей."""

from .document import Document, DocumentId
from .chunk import Chunk, ChunkId

__all__ = [
    "Document",
    "DocumentId",
    "Chunk",
    "ChunkId"
]
