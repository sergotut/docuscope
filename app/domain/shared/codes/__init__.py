"""Базовый тип для всех варнингов в системе.

Содержит только общий тип WarningCode. Конкретные коды находятся
в соответствующих доменных контекстах.
"""

from .warnings import WarningCode as WarningCode

__all__ = [
    "WarningCode",
]
