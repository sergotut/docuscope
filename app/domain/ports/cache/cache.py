"""Порт (интерфейс) ключ-значение поверх движка кэша.

Байтовая семантика на границе (сериализация — уровнем выше).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import CacheHealthReport

__all__ = ["CachePort"]


@runtime_checkable
class CachePort(Protocol):
    """Простой KV-интерфейс кэша с байтовыми значениями."""

    async def ping(self) -> bool:
        """Проверяет доступность кэша.

        Returns:
            bool: True, если ответ получен.
        """
        ...

    async def get(self, key: str) -> bytes | None:
        """Возвращает значение по ключу.

        Args:
            key (str): Ключ.

        Returns:
            bytes | None: Значение или None, если ключ отсутствует.
        """
        ...

    async def set(
        self,
        key: str,
        value: bytes,
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        """Сохраняет значение по ключу с опциональным TTL.

        Args:
            key (str): Ключ.
            value (bytes): Сохраняемое значение.
            ttl_seconds (int | None): Время жизни ключа в секундах.
        """
        ...

    async def delete(self, key: str) -> bool:
        """Удаляет ключ.

        Args:
            key (str): Ключ.

        Returns:
            bool: True, если ключ существовал и был удалён.
        """
        ...

    async def expire(self, key: str, ttl_seconds: int) -> bool:
        """Устанавливает TTL для существующего ключа.

        Args:
            key (str): Ключ.
            ttl_seconds (int): Новое время жизни ключа в секундах.

        Returns:
            bool: True, если TTL был установлен.
        """
        ...

    async def incr(self, key: str, amount: int = 1) -> int:
        """Атомарно увеличивает числовое значение ключа.

        Если ключ отсутствует, создаёт его со значением amount.

        Args:
            key (str): Ключ счётчика.
            amount (int): Величина инкремента.

        Returns:
            int: Новое значение счётчика.
        """
        ...

    async def is_healthy(self) -> bool:
        """Быстрый health-check.

        Returns:
            bool: True, если базовые операции выполняются успешно.
        """
        ...

    async def health(self) -> CacheHealthReport:
        """Расширенный health-отчёт.

        Returns:
            CacheHealthReport: Техинформация и метрики состояния кэша.
        """
        ...
