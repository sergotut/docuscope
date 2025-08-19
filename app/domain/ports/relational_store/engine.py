"""Порт (интерфейс) движка реляционной БД или пула соединений.

Предоставляет:
- управление жизненным циклом (connect, close, is_connected);
- выдачу соединения через acquire();
- health-check (is_healthy) и расширенный отчёт (health).
"""

from __future__ import annotations

from typing import AsyncContextManager, Protocol, runtime_checkable

from app.domain.model.diagnostics import RelationalDBHealthReport
from .connection import RelConnection

__all__ = ["RelationalEnginePort"]


@runtime_checkable
class RelationalEnginePort(Protocol):
    """Порт движка реляционной БД/пула соединений."""

    async def connect(self) -> None:
        """Открывает соединение(я) или инициализирует пул."""
        ...

    async def close(self) -> None:
        """Закрывает соединение(я) или останавливает пул."""
        ...

    def is_connected(self) -> bool:
        """Возвращает признак активного подключения.

        Returns:
            bool: True, если подключение установлено.
        """
        ...

    def acquire(self) -> AsyncContextManager[RelConnection]:
        """Возвращает асинхронный контекст с соединением.

        Returns:
            AsyncContextManager[RelConnection]: Контекст с активным соединением.
        """
        ...

    async def is_healthy(self) -> bool:
        """Быстрый health-check движка.

        Returns:
            bool: True, если базовые операции выполняются.
        """
        ...

    async def health(self) -> RelationalDBHealthReport:
        """Расширенный health-отчёт.

        Returns:
            RelationalDBHealthReport: Техинформация и метрики движка.
        """
        ...
