"""Движок PostgreSQL поверх asyncpg-пула.

Реализация RelationalEnginePort c acquire() через @asynccontextmanager.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncIterator, cast

import structlog

from app.domain.model.diagnostics import RelationalDBHealthReport
from app.domain.ports.relational_store import RelConnection, RelationalEnginePort
from app.infrastructure.adapters.outbound.relational_store.postgres_client import (  # noqa: E501
    AsyncPGPool,
    mask_dsn,
)

__all__ = ["PostgresEngine"]

logger = structlog.get_logger(__name__)


class PostgresEngine(RelationalEnginePort):
    """Движок PostgreSQL поверх asyncpg-пула."""

    def __init__(
        self,
        dsn: str,
        *,
        min_size: int = 1,
        max_size: int = 10,
        timeout: float | None = None,
    ) -> None:
        """Создаёт движок.

        Args:
            dsn (str): Строка подключения.
            min_size (int): Минимальный размер пула.
            max_size (int): Максимальный размер пула.
            timeout (float | None): Таймаут создания пула, сек.
        """
        self._dsn = dsn
        self._pool = AsyncPGPool(
            dsn=dsn,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
        )
        logger.info(
            "postgres engine init",
            min_pool=min_size,
            max_pool=max_size,
            timeout=timeout,
        )

    async def connect(self) -> None:
        """Инициализирует пул соединений."""
        await self._pool.connect()

    async def close(self) -> None:
        """Закрывает пул соединений."""
        await self._pool.close()

    def is_connected(self) -> bool:
        """Возвращает признак активного подключения.

        Returns:
            bool: True, если пул инициализирован.
        """
        return self._pool.is_connected()

    def acquire(self) -> AsyncContextManager[RelConnection]:
        """Возвращает асинхронный контекст с соединением.

        Returns:
            AsyncContextManager[RelConnection]: Контекст для async with.
        """

        @asynccontextmanager
        async def _ctx() -> AsyncIterator[RelConnection]:
            conn = await self._pool.acquire()
            try:
                yield cast(RelConnection, conn)
            finally:
                await self._pool.release(conn)

        return _ctx()

    async def is_healthy(self) -> bool:
        """Быстрый health-check.

        Returns:
            bool: True, если простейший запрос выполняется.
        """
        try:
            async with self.acquire() as c:
                await c.fetchval("select 1")
            return True
        except Exception:  # noqa: BLE001
            logger.warning("postgres is_healthy failed", error=str(exc))
            return False

    async def health(self) -> RelationalDBHealthReport:
        """Расширенный health-отчёт.

        Returns:
            RelationalDBHealthReport: Сводные метрики движка.
        """
        version: str = ""
        latency_ms: float = 0.0
        database: str = ""
        role: str = "unknown"
        readonly = False
        max_conn = 0
        num_backends = 0
        xact_commit = 0
        xact_rollback = 0
        buf_hit_ratio = 0.0
        uptime_seconds = 0

        # latency
        try:
            t0 = time.perf_counter()
            async with self.acquire() as c:
                await c.fetchval("select 1")
            latency_ms = (time.perf_counter() - t0) * 1000.0
        except Exception:  # noqa: BLE001
            logger.warning("postgres latency check failed", error=str(exc))

        try:
            async with self.acquire() as c:
                version = str(
                    await c.fetchval(
                        "select current_setting('server_version', true)"
                    )
                )
                database = str(await c.fetchval("select current_database()"))

                is_recovery = await c.fetchval("select pg_is_in_recovery()")
                role = "replica" if is_recovery else "primary"

                ro_setting = await c.fetchval(
                    "select current_setting('transaction_read_only', true)"
                )
                readonly = str(ro_setting).lower() in {"on", "true", "1"}

                max_conn = int(
                    await c.fetchval(
                        "select current_setting('max_connections')::int"
                    )
                    or 0
                )

                row = await c.fetchrow(
                    """
                    select numbackends, xact_commit, xact_rollback,
                           blks_read, blks_hit
                      from pg_stat_database
                     where datname = current_database()
                    """
                )
                if row:
                    num_backends = int(row.get("numbackends", 0) or 0)
                    xact_commit = int(row.get("xact_commit", 0) or 0)
                    xact_rollback = int(row.get("xact_rollback", 0) or 0)
                    blks_read = int(row.get("blks_read", 0) or 0)
                    blks_hit = int(row.get("blks_hit", 0) or 0)
                    denom = blks_hit + blks_read
                    buf_hit_ratio = (blks_hit / denom) if denom else 0.0

                up = await c.fetchval(
                    """
                    select extract(epoch from
                           (now() - pg_postmaster_start_time()))::bigint
                    """
                )
                uptime_seconds = int(up or 0)
        except Exception:  # noqa: BLE001
            logger.warning("postgres health metrics failed", error=str(exc))

        min_s, max_s, in_use = self._pool.stats
        return {
            "engine": "asyncpg",
            "version": version,
            "dsn": mask_dsn(self._dsn),
            "database": database,
            "status": "ok" if version else "degraded",
            "pool_min": min_s,
            "pool_max": max_s,
            "pool_in_use": in_use,
            "latency_ms": latency_ms,
            # расширенные
            "role": role,
            "readonly": readonly,
            "max_connections": max_conn,
            "num_backends": num_backends,
            "xact_commit": xact_commit,
            "xact_rollback": xact_rollback,
            "buffers_cache_hit_ratio": buf_hit_ratio,
            "uptime_seconds": uptime_seconds,
        }
