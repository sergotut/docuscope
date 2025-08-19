"""Обёртка пула asyncpg с минимальным API.

Даёт единый интерфейс для движка: connect/close, acquire/release и
простую статистику пула.
"""

from __future__ import annotations

from typing import Tuple

import asyncpg

from .protocols import PgConnectionLike

__all__ = ["AsyncPGPool"]


class AsyncPGPool:
    """Пул соединений asyncpg с минимальным API.

    Attributes:
        dsn (str): Строка подключения.
        min_size (int): Минимальный размер пула.
        max_size (int): Максимальный размер пула.
        timeout (float | None): Таймаут создания пула, сек.
    """

    def __init__(
        self,
        *,
        dsn: str,
        min_size: int = 1,
        max_size: int = 10,
        timeout: float | None = None,
    ) -> None:
        """Создаёт пул, без подключения.

        Args:
            dsn (str): DSN для asyncpg.
            min_size (int): Минимальный размер пула.
            max_size (int): Максимальный размер пула.
            timeout (float | None): Таймаут создания пула, сек.
        """
        self._dsn = dsn
        self._min = int(min_size)
        self._max = int(max_size)
        self._timeout = timeout
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Инициализирует пул соединений."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min,
                max_size=self._max,
                timeout=self._timeout,
            )

    async def close(self) -> None:
        """Закрывает пул соединений."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def is_connected(self) -> bool:
        """Возвращает признак активного пула.

        Returns:
            bool: True, если пул инициализирован.
        """
        return self._pool is not None

    async def acquire(self) -> PgConnectionLike:
        """Выдаёт соединение из пула.

        Returns:
            PgConnectionLike: Соединение драйвера.
        """
        if self._pool is None:
            raise RuntimeError("AsyncPG: Pool is not connected")
        return await self._pool.acquire()

    async def release(self, conn: PgConnectionLike) -> None:
        """Возвращает соединение в пул.

        Args:
            conn (PgConnectionLike): Ранее выданное соединение.
        """
        assert self._pool is not None
        await self._pool.release(conn)  # type: ignore[arg-type]

    @property
    def stats(self) -> Tuple[int, int, int]:
        """Возвращает (min_size, max_size, in_use).

        Returns:
            tuple[int, int, int]: Минимум, максимум и занятые соединения.
        """
        pool = self._pool

        if pool is None:
            return (self._min, self._max, 0)
        try:
            in_use = pool.get_size() - pool.get_idle_size()
        except Exception:
            in_use = 0
        return (self._min, self._max, int(in_use))
