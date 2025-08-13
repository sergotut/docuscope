"""Пакет model: вложенные неймспейсы доменных моделей.

Экспортируются подпакеты:
    - documents
    - retrieval
    - media
    - shared

Использование:
    from app.domain.model import documents
    doc = documents.Document(...)
"""

from . import documents as documents
from . import media as media
from . import retrieval as retrieval
from . import shared as shared
from . import diagnostics as diagnostics

__all__ = [
    "documents",
    "retrieval",
    "media",
    "shared",
    "diagnostics"
]
