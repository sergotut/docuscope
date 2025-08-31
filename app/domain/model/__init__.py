"""Пакет model: вложенные неймспейсы доменных моделей.

Экспортируются подпакеты:
    - collections
    - diagnostics
    - documents
    - media
    - retrieval
    - shared
    - validation
    - vector_store

Использование:
    from app.domain.model import documents
    doc = documents.Document(...)
"""

from . import collections as collections
from . import diagnostics as diagnostics
from . import documents as documents
from . import media as media
from . import retrieval as retrieval
from . import shared as shared
from . import validation as validation
from . import vector_store as vector_store

__all__ = [
    "collections",
    "diagnostics",
    "documents",
    "media",
    "retrieval",
    "shared",
    "validation",
    "vector_store",
]
