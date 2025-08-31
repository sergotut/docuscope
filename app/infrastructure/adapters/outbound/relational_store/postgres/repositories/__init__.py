"""Пакет repositories: публичные реэкспорты."""

from .collections import PostgresCollectionRepository
from .documents import PostgresDocumentMetaRepository

__all__ = [
    "PostgresCollectionRepository",
    "PostgresDocumentMetaRepository",
]
