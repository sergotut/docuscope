"""Pg-специфичный протокол соединения (postgres-клиент).

Минимальный контракт для адаптера: execute/fetch* и фабрика транзакций.
Намеренно небольшой и совместимый с asyncpg-подобными драйверами.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, AsyncContextManager, Protocol, runtime_checkable

__all__ = ["PgConnectionLike"]


@runtime_checkable
class PgConnectionLike(Protocol):
    """Минимальный интерфейс pg-соединения."""

    async def execute(self, query: str, *args: Any) -> Any:
        """Выполняет команду без выборки."""
        ...

    async def fetch(self, query: str, *args: Any) -> list[Mapping[str, Any]]:
        """Возвращает все строки результата."""
        ...

    async def fetchrow(
        self,
        query: str,
        *args: Any,
    ) -> Mapping[str, Any] | None:
        """Возвращает одну строку результата или None."""
        ...

    async def fetchval(self, query: str, *args: Any) -> Any:
        """Возвращает одно скалярное значение."""
        ...

    def transaction(self) -> AsyncContextManager[object]:
        """Возвращает асинхронный контекстный менеджер транзакции."""
        ...
