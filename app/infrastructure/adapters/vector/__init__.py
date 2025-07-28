"""DI-адаптеры векторных хранилищ."""

from .null import NullVectorStore
from .qdrant import QdrantVectorStoreAdapter

__all__ = [
    "QdrantVectorStoreAdapter",
    "NullVectorStore",
]
