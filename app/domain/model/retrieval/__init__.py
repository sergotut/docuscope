"""Пакет retrieval: публичные реэкспорты моделей эмбеддингов и поиска."""

from .embedding import EmbeddingVector, EmbeddingBatch
from .search import ScoredChunk, Query

__all__ = [
    "EmbeddingVector",
    "EmbeddingBatch",
    "ScoredChunk",
    "Query"
]
