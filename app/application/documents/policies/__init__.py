"""Пакет политик для документов."""

from __future__ import annotations

from .input_validation import DocumentInputConstraints, DocumentInputValidationService

__all__ = [
    "DocumentInputConstraints",
    "DocumentInputValidationService",
]
