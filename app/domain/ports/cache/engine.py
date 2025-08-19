"""Порт движка кэша (Redis-подобный).

Определяет унифицированный интерфейс для подключения к кэшу, закрытия
соединения, проверки доступности и получения расширенного health-отчёта.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import CacheHealthReport

__all__ = ["CacheEnginePort"]


@runtime_checkable
class CacheEnginePort(Protocol):
    """Порт движка кэша."""

    async def connect(self) -> None:
        """Открывает соединение или инициализирует клиент."""
        ...

    async def close(self) -> None:
        """Закрывает соединение и освобождает ресурсы клиента."""
        ...

    def is_connected(self) -> bool:
        """Возвращает признак активного подключения.

        Returns:
            bool: True, если клиент инициализирован и соединение активно.
        """
        ...

    async def is_healthy(self) -> bool:
        """Быстрый health-check.

        Returns:
            bool: True, если базовая команда к кэшу выполняется успешно.
        """
        ...

    async def health(self) -> CacheHealthReport:
        """Расширенный health-отчёт.

        Returns:
            CacheHealthReport: Техинформация и метрики состояния кэша.
        """
        ...
