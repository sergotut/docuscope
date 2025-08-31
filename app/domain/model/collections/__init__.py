"""Пакет collections: публичные реэкспорты доменных моделей коллекций."""

from .collection import (
    CollectionMeta,
    CollectionName,
    CollectionStatus,
)

__all__ = [
    "CollectionName",
    "CollectionMeta",
    "CollectionStatus",
]
