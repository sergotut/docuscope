"""Порт (интерфейс) соединения реляционной БД.

Используется репозиториями и Unit of Work. Повторяет базовые операции
асинхронных драйверов: execute, fetch*, а также фабрику транзакций.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, AsyncContextManager, Protocol, runtime_checkable

__all__ = ["RelConnection"]


@runtime_checkable
class RelConnection(Protocol):
    """Минимальный контракт соединения для репозиториев и UoW.

    Методы повторяют типичные операции асинхронных драйверов
    (execute, fetch, fetchrow, fetchval) и предоставляют transaction.
    """

    async def execute(self, sql: str, *args: Any) -> Any:
        """Выполняет команду без выборки.

        Args:
            sql (str): SQL-выражение.
            *args (Any): Позиционные параметры запроса.

        Returns:
            Any: Результат выполнения (зависит от драйвера).
        """
        ...

    async def fetch(self, sql: str, *args: Any) -> list[Mapping[str, Any]]:
        """Возвращает все строки результата.

        Args:
            sql (str): SQL-выражение (SELECT ...).
            *args (Any): Параметры запроса.

        Returns:
            list[Mapping[str, Any]]: Список строк в виде отображений.
        """
        ...

    async def fetchrow(self, sql: str, *args: Any) -> Mapping[str, Any] | None:
        """Возвращает одну строку результата или None.

        Args:
            sql (str): SQL-выражение (SELECT ...).
            *args (Any): Параметры запроса.

        Returns:
            Mapping[str, Any] | None: Одна строка или None.
        """
        ...

    async def fetchval(self, sql: str, *args: Any) -> Any:
        """Возвращает одно скалярное значение.

        Args:
            sql (str): SQL-выражение (SELECT ...).
            *args (Any): Параметры запроса.

        Returns:
            Any: Скалярное значение первой колонки первой строки.
        """
        ...

    def transaction(self) -> AsyncContextManager[object]:
        """Возвращает асинхронный контекстный менеджер транзакции.

        Returns:
            AsyncContextManager[object]: Контекст транзакции.
        """
        ...
