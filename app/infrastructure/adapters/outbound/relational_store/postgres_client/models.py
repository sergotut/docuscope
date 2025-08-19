"""Модели клиента Postgres: вспомогательные value-объекты.

Содержит статистику пула соединений.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["PoolStats"]


@dataclass(slots=True)
class PoolStats:
    """Статистика пула соединений.

    Attributes:
        min_size (int): Минимальный размер пула.
        max_size (int): Максимальный размер пула.
        in_use (int): Текущее количество занятых соединений.
    """

    min_size: int
    max_size: int
    in_use: int
