"""Публичный API инфраструктурного слоя приложения.

Экспортируется только DI-контейнер.
"""

from .di_container import Container

__all__ = [
    "Container",
]
