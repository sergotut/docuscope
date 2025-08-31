"""Shim: реэкспорт адаптера Qdrant из подпакета qdrant.

Служит для обратной совместимости.
"""

from .qdrant_client import QdrantVectorStore

__all__ = ["QdrantVectorStore"]
