"""
DI-адаптеры векторных хранилищ.
"""

from .qdrant import QdrantVectorStoreAdapter
from .null import NullVectorStore

__all__ = [
    "QdrantVectorStoreAdapter",
    "NullVectorStore",
]
