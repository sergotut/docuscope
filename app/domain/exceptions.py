"""Общая иерархия ошибок сервиса «Документоскоп»."""

from __future__ import annotations

__all__ = [
    "DocuscopeError",
    "StorageError",
    "VectorStoreError",
    "DomainValidationError",
    "TokenError",
]


class DocuscopeError(Exception):
    """Базовое исключение Документоскопа."""


class StorageError(DocuscopeError):
    """Ошибки, возникающие при работе с файловым хранилищем."""


class VectorStoreError(DocuscopeError):
    """Ошибки, возникающие при операциях с векторным хранилищем."""


class DomainValidationError(DocuscopeError):
    """Ошибки валидации доменных моделей и их аргументов."""


class TokenError(DomainValidationError):
    """Ошибки, связанные с токенами и их подсчётом."""
