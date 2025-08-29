"""Пул и обёртка клиента Redis (redis.asyncio).

Дает унифицированный интерфейс RedisClientLike и поддерживает:
- опциональный PING при подключении (test_on_connect);
- одноразовый auto-reconnect при сетевых ошибках;
- контекстный менеджер (async with RedisPool(...));
- прокидку client_kwargs в Redis.from_url() (таймауты, SSL и пр.).
"""

from __future__ import annotations

from collections.abc import Awaitable, Mapping
from typing import Any, Callable

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnError
from redis.exceptions import TimeoutError as RedisTimeoutError

from .protocols import RedisClientLike

__all__ = ["RedisPool"]


class _ClientWrapper(RedisClientLike):
    """Обёртка над redis.asyncio.Redis под RedisClientLike с авто-reconnect.

    Attributes:
        _get (Callable[[], Redis]): Фабрика для текущего клиента.
        _reconnect (Callable[[], Awaitable[None]]): Процедура переподключения.
    """

    def __init__(
        self,
        *,
        get_client: Callable[[], Redis],
        reconnect: Callable[[], Awaitable[None]],
    ) -> None:
        """Инициализирует обёртку.

        Args:
            get_client (Callable[[], Redis]): Фабрика, возвращающая текущий клиент.
            reconnect (Callable[[], Awaitable[None]]): Корутинa переподключения,
                вызывается перед повторной попыткой после сетевой ошибки.
        """
        self._get = get_client
        self._reconnect = reconnect

    async def _call(self, fn: Callable[[Redis], Awaitable[Any]]) -> Any:
        """Вызывает fn с разовым retry после reconnect при сетевой ошибке.

        Args:
            fn (Callable[[Redis], Awaitable[Any]]): Операция над клиентом.

        Returns:
            Any: Результат вызова операции.
        """
        try:
            return await fn(self._get())
        except (RedisConnError, RedisTimeoutError, OSError):
            await self._reconnect()
            return await fn(self._get())

    async def ping(self) -> bool:
        """Выполняет PING.

        Returns:
            bool: True, если ответ успешен.
        """
        return bool(await self._call(lambda c: c.ping()))

    async def get(self, key: str) -> bytes | None:
        """Читает значение по ключу.

        Args:
            key (str): Ключ.

        Returns:
            bytes | None: Значение или None.
        """
        res = await self._call(lambda c: c.get(key))
        return res  # type: ignore[return-value]

    async def set(
        self,
        key: str,
        value: bytes,
        ttl_seconds: int | None = None,
    ) -> None:
        """Записывает значение с TTL.

        Args:
            key (str): Ключ.
            value (bytes): Значение.
            ttl_seconds (int | None): TTL в секундах.
        """
        await self._call(lambda c: c.set(key, value, ex=ttl_seconds))

    async def delete(self, key: str) -> int:
        """Удаляет ключ.

        Args:
            key (str): Ключ.

        Returns:
            int: Количество удалённых ключей (0 или 1).
        """
        res = await self._call(lambda c: c.delete(key))
        return int(res)

    async def expire(self, key: str, ttl_seconds: int) -> bool:
        """Устанавливает TTL для ключа.

        Args:
            key (str): Ключ.
            ttl_seconds (int): Время жизни в секундах.

        Returns:
            bool: True, если TTL установлен.
        """
        res = await self._call(lambda c: c.expire(key, ttl_seconds))
        return bool(res)

    async def incr(self, key: str, amount: int = 1) -> int:
        """Атомарно увеличивает счётчик.

        Args:
            key (str): Ключ.
            amount (int): Величина инкремента.

        Returns:
            int: Новое значение счётчика.
        """
        res = await self._call(lambda c: c.incr(key, amount))
        return int(res)

    async def info(self) -> dict[str, Any]:
        """Возвращает информацию о сервере и статистику.

        Returns:
            dict[str, Any]: Карта метрик и настроек.
        """
        res = await self._call(lambda c: c.info())
        return dict(res)


class RedisPool:
    """Управляет подключением и выдаёт клиента с унифицированным API.

    Attributes:
        _url (str): Redis URL.
        _test_on_connect (bool): Делать PING после connect().
        _client_kwargs (dict[str, Any]): Параметры Redis.from_url().
    """

    def __init__(
        self,
        url: str,
        *,
        test_on_connect: bool = True,
        client_kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        """Создаёт пул.

        Args:
            url (str): Redis URL.
            test_on_connect (bool): Выполнить PING после connect().
            client_kwargs (Mapping[str, Any] | None): Доп. аргументы для
                Redis.from_url (например, socket_timeout, ssl).
        """
        self._url = url
        self._test_on_connect = bool(test_on_connect)
        self._client_kwargs = dict(client_kwargs or {})
        self._client_kwargs.setdefault("decode_responses", False)

        self._client: Redis | None = None
        self._wrapped: _ClientWrapper | None = None

    async def __aenter__(self) -> RedisPool:
        """Открывает соединение при входе в контекст."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Закрывает соединение при выходе из контекста."""
        await self.close()

    def _build_client(self) -> Redis:
        """Создаёт экземпляр Redis из URL и параметров.

        Returns:
            Redis: Низкоуровневый клиент redis.asyncio.
        """
        return Redis.from_url(self._url, **self._client_kwargs)

    def _get_current(self) -> Redis:
        """Возвращает текущий активный клиент.

        Returns:
            Redis: Активный клиент.

        Raises:
            RuntimeError: Если соединение не установлено.
        """
        if self._client is None:
            msg = "Redis is not connected"
            raise RuntimeError(msg)
        return self._client

    async def _reconnect(self) -> None:
        """Переподключается: close() → connect()."""
        await self.close()
        await self.connect()

    async def connect(self) -> None:
        """Инициализирует подключение (опц. проверка доступности)."""
        if self._client is not None:
            return

        self._client = self._build_client()
        if self._test_on_connect:
            await self._client.ping()

        self._wrapped = _ClientWrapper(
            get_client=self._get_current,
            reconnect=self._reconnect,
        )

    async def close(self) -> None:
        """Закрывает соединение (идемпотентно)."""
        if self._client is not None:
            try:
                await self._client.aclose()
            finally:
                self._client = None
                self._wrapped = None

    def is_connected(self) -> bool:
        """Возвращает признак активного подключения.

        Returns:
            bool: True, если клиент инициализирован.
        """
        return self._client is not None

    def client(self) -> RedisClientLike:
        """Возвращает клиента с унифицированным интерфейсом.

        Returns:
            RedisClientLike: Обёрнутый клиент Redis.

        Raises:
            RuntimeError: Если подключение не установлено.
        """
        if self._wrapped is None:
            msg = "Redis is not connected"
            raise RuntimeError(msg)
        return self._wrapped
