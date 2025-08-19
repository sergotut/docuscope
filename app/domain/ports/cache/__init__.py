"""Пакет cache: доменных портов (интерфейсов)."""

from .engine import CacheEnginePort
from .cache import CachePort


__all__ = [
    "CacheEnginePort",
    "CachePort",
]
