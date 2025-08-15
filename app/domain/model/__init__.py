"""Пакет model: вложенные неймспейсы доменных моделей.

Экспортируются подпакеты:
    - documents
    - retrieval
    - media
    - shared
    - diagnostics
    - vector_store

Использование:
    from app.domain.model import documents
    doc = documents.Document(...)
"""

from . import documents as documents
from . import media as media
from . import retrieval as retrieval
from . import shared as shared
from . import diagnostics as diagnostics
from . import vector_store as vector_store

__all__ = [
    "documents",
    "retrieval",
    "media",
    "shared",
    "diagnostics",
    "vector_store",
]
