"""Порт репозитория коллекций.

Интерфейс задаёт минимальные операции поверх первичного хранилища:
создание коллекции с TTL, чтение метаданных, одноразовое запечатывание,
список просроченных коллекций и каскадное удаление.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

from app.domain.model.collections import (
    CollectionMeta,
    CollectionName,
)

__all__ = ["CollectionRepositoryPort"]


@runtime_checkable
class CollectionRepositoryPort(Protocol):
    """Репозиторий коллекций с политикой TTL и «одна загрузка»."""

    async def create(
        self,
        name: CollectionName,
        ttl: timedelta,
        now: datetime,
    ) -> bool:
        """Создаёт коллекцию с заданным TTL.

        Если коллекция уже существует, операция не выполняется.

        Args:
            name (CollectionName): Имя коллекции.
            ttl (timedelta): Время жизни коллекции.
            now (datetime): Текущее время, точка отсчёта TTL.

        Returns:
            bool: True, если создана; False, если уже существовала.
        """

    async def get(self, name: CollectionName) -> CollectionMeta | None:
        """Возвращает метаданные коллекции.

        Args:
            name (CollectionName): Имя коллекции.

        Returns:
            CollectionMeta | None: Метаданные коллекции или None,
            если не найдена.
        """

    async def seal_uploaded_once(self, name: CollectionName, now: datetime) -> bool:
        """Атомарно помечает первую и единственную загрузку.

        Возвращает False, если коллекция уже была запечатана ранее.

        Args:
            name (CollectionName): Имя коллекции.
            now (datetime): Время запечатывания.

        Returns:
            bool: True, если запечатали; False, если уже была запечатана.
        """

    async def list_expired(self, now: datetime, limit: int) -> list[CollectionName]:
        """Возвращает имена просроченных коллекций.

        Args:
            now (datetime): Текущее время для проверки TTL.
            limit (int): Максимальное количество имён в выдаче.

        Returns:
            list[CollectionName]: Список имён просроченных коллекций.
        """

    async def delete_cascade(self, name: CollectionName) -> None:
        """Удаляет коллекцию и связанные записи.

        Args:
            name (CollectionName): Имя коллекции.
        """
