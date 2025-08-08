"""Общая иерархия ошибок сервиса «Документоскоп»."""

from __future__ import annotations


class DocuscopeError(Exception):
    """Базовое исключение Документоскопа."""


class StorageError(DocuscopeError):
    """Ошибки, возникающие при работе с файловым хранилищем."""


class VectorStoreError(DocuscopeError):
    """Ошибки, возникающие при операциях с векторным хранилищем."""
