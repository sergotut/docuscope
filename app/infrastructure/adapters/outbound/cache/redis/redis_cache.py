"""Адаптер CachePort на базе RedisEngine."""

from __future__ import annotations

from app.domain.model.diagnostics import CacheHealthReport
from app.domain.ports.cache import CachePort

from .engine import RedisEngine

__all__ = ["RedisCache"]


class RedisCache(CachePort):
    """Реализация CachePort поверх Redis."""

    def __init__(self, engine: RedisEngine) -> None:
        """Создаёт адаптер.

        Args:
            engine (RedisEngine): Инициализированный движок Redis.
        """
        self._engine = engine

    async def ping(self) -> bool:
        """Проверяет доступность кэша.

        Returns:
            bool: True, если Redis отвечает.
        """
        return await self._engine.is_healthy()

    async def get(self, key: str) -> bytes | None:
        """Читает значение по ключу.

        Args:
            key (str): Ключ.

        Returns:
            bytes | None: Значение или None.
        """
        return await self._engine.client().get(key)

    async def set(
        self,
        key: str,
        value: bytes,
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        """Записывает значение по ключу с TTL (опционально).

        Args:
            key (str): Ключ.
            value (bytes): Значение.
            ttl_seconds (int | None): TTL в секундах.
        """
        await self._engine.client().set(key, value, ttl_seconds=ttl_seconds)

    async def delete(self, key: str) -> bool:
        """Удаляет ключ.

        Args:
            key (str): Ключ.

        Returns:
            bool: True, если ключ был удалён.
        """
        return (await self._engine.client().delete(key)) > 0

    async def expire(self, key: str, ttl_seconds: int) -> bool:
        """Устанавливает TTL для ключа.

        Args:
            key (str): Ключ.
            ttl_seconds (int): Время жизни в секундах.

        Returns:
            bool: True, если TTL установлен.
        """
        return bool(await self._engine.client().expire(key, ttl_seconds))

    async def incr(self, key: str, amount: int = 1) -> int:
        """Атомарно увеличивает счётчик.

        Args:
            key (str): Ключ.
            amount (int): Величина инкремента.

        Returns:
            int: Новое значение счётчика.
        """
        return int(await self._engine.client().incr(key, amount))

    async def is_healthy(self) -> bool:
        """Быстрый health-check.

        Returns:
            bool: Признак доступности Redis.
        """
        return await self._engine.is_healthy()

    async def health(self) -> CacheHealthReport:
        """Возвращает расширенный health-отчёт.

        Returns:
            CacheHealthReport: Метрики и техинформация Redis.
        """
        return await self._engine.health()
