"""Пакет validation: публичные реэкспорты."""

from .names import validate_name
from .uuid import validate_uuid_like

__all__ = [
    "validate_name",
    "validate_uuid_like",
]
