"""Движок Redis поверх пул-клиента.

Реализует CacheEnginePort: connect/close/is_connected, быстрый is_healthy
и расширенный health(). Даёт доступ к клиенту через .client().
"""

from __future__ import annotations

import time

from app.domain.model.diagnostics import CacheHealthReport
from app.domain.ports.cache import CacheEnginePort
from app.infrastructure.adapters.outbound.cache.redis_client import (
    RedisPool,
    RedisClientLike,
    mask_url,
)

__all__ = ["RedisEngine"]


class RedisEngine(CacheEnginePort):
    """Движок Redis поверх пул-клиента."""

    def __init__(self, url: str) -> None:
        """Создаёт движок.

        Args:
            url (str): URL подключения к Redis.
        """
        self._url = url
        self._pool = RedisPool(url)

    async def connect(self) -> None:
        """Инициализирует пул соединений."""
        await self._pool.connect()

    async def close(self) -> None:
        """Закрывает пул и освобождает ресурсы."""
        await self._pool.close()

    def is_connected(self) -> bool:
        """Возвращает признак активного подключения.

        Returns:
            bool: True, если пул инициализирован.
        """
        return self._pool.is_connected()

    def client(self) -> RedisClientLike:
        """Возвращает клиент Redis из пула.

        Returns:
            RedisClientLike: Клиент для выполнения команд.
        """
        return self._pool.client()

    async def is_healthy(self) -> bool:
        """Быстрый health-check через PING.

        Returns:
            bool: True, если PING успешен.
        """
        try:
            return bool(await self.client().ping())
        except Exception:  # noqa: BLE001
            return False

    async def health(self) -> CacheHealthReport:
        """Расширенный health-отчёт.

        Returns:
            CacheHealthReport: Метрики и техинформация Redis.
        """
        latency_ms: float = 0.0
        version: str = ""
        role: str = ""
        uptime_seconds = 0
        used_memory_bytes = 0
        connected_clients = 0
        total_commands_processed = 0
        keyspace_keys = 0
        keyspace_expires = 0
        hit_ratio = 0.0

        try:
            c = self.client()
            t0 = time.perf_counter()
            await c.ping()
            latency_ms = (time.perf_counter() - t0) * 1000.0

            info = await c.info()
            version = str(info.get("redis_version", ""))
            role = str(info.get("role", "")) or "n/a"
            uptime_seconds = int(info.get("uptime_in_seconds", 0) or 0)
            used_memory_bytes = int(info.get("used_memory", 0) or 0)
            connected_clients = int(info.get("connected_clients", 0) or 0)
            total_commands_processed = int(
                info.get("total_commands_processed", 0) or 0
            )
            hits = int(info.get("keyspace_hits", 0) or 0)
            misses = int(info.get("keyspace_misses", 0) or 0)
            denom = hits + misses
            hit_ratio = (hits / denom) if denom else 0.0
            db0 = info.get("db0") or {}
            keyspace_keys = int(db0.get("keys", 0) or 0)
            keyspace_expires = int(db0.get("expires", 0) or 0)
        except Exception:  # noqa: BLE001
            pass

        return {
            "engine": "redis.asyncio",
            "version": version,
            "dsn": mask_url(self._url),
            "role": role or "n/a",
            "status": "ok" if latency_ms > 0 else "degraded",
            "latency_ms": latency_ms,
            "db": 0,
            # расширенные
            "uptime_seconds": uptime_seconds,
            "used_memory_bytes": used_memory_bytes,
            "connected_clients": connected_clients,
            "total_commands_processed": total_commands_processed,
            "keyspace_keys": keyspace_keys,
            "keyspace_expires": keyspace_expires,
            "hit_ratio": hit_ratio,
        }
