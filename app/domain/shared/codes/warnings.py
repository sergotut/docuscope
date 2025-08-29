"""Базовый тип для всех варнингов в системе.

Содержит только общий тип WarningCode. Конкретные коды находятся
в соответствующих доменных контекстах.
"""

from __future__ import annotations

from typing import TypeAlias

__all__ = [
    "WarningCode",
]

# Общий тип для всех предупреждений в системе
WarningCode: TypeAlias = str
