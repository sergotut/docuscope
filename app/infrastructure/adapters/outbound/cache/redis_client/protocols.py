"""Протокол асинхронного клиента Redis (sdk-специфичный).

Минимальный контракт под Redis: ping/get/set/delete/expire/incr/info.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ["RedisClientLike"]


@runtime_checkable
class RedisClientLike(Protocol):
    """Минимальный интерфейс Redis-клиента."""

    async def ping(self) -> bool:
        """Проверяет доступность сервера.

        Returns:
            bool: True, если ответ получен.
        """
        ...

    async def get(self, key: str) -> bytes | None:
        """Читает значение по ключу.

        Args:
            key (str): Ключ.

        Returns:
            bytes | None: Значение в байтах или None, если ключ отсутствует.
        """
        ...

    async def set(
        self,
        key: str,
        value: bytes,
        ttl_seconds: int | None = None,
    ) -> None:
        """Сохраняет значение по ключу с необязательным TTL.

        Args:
            key (str): Ключ.
            value (bytes): Байтовое значение.
            ttl_seconds (int | None): Время жизни ключа в секундах.
        """
        ...

    async def delete(self, key: str) -> int:
        """Удаляет ключ.

        Args:
            key (str): Ключ.

        Returns:
            int: Количество удалённых ключей (0 или 1).
        """
        ...

    async def expire(self, key: str, ttl_seconds: int) -> bool:
        """Устанавливает TTL для ключа.

        Args:
            key (str): Ключ.
            ttl_seconds (int): Время жизни ключа в секундах.

        Returns:
            bool: True, если TTL установлен.
        """
        ...

    async def incr(self, key: str, amount: int = 1) -> int:
        """Атомарно увеличивает числовое значение по ключу.

        Args:
            key (str): Ключ.
            amount (int): Величина инкремента.

        Returns:
            int: Новое значение счётчика.
        """
        ...

    async def info(self) -> dict[str, Any]:
        """Возвращает информацию о сервере и статистику.

        Returns:
            dict[str, Any]: Карта метрик и настроек.
        """
        ...
