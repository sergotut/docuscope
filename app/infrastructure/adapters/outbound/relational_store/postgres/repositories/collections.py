"""Репозиторий коллекций для PostgreSQL."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.domain.model.collections import CollectionMeta, CollectionName
from app.domain.ports.relational_store import CollectionRepositoryPort, RelConnection

__all__ = ["PostgresCollectionRepository"]


class PostgresCollectionRepository(CollectionRepositoryPort):
    """Postgres-репозиторий коллекций под политику TTL и «одна загрузка»."""

    def __init__(self, conn: RelConnection) -> None:
        """Инициализирует репозиторий.

        Args:
            conn (RelConnection): Активное соединение с БД.
        """
        self._c = conn

    async def create(
        self,
        name: CollectionName,
        ttl: timedelta,
        now: datetime,
    ) -> bool:
        """Создаёт коллекцию с расчётом expire_at = now + ttl.

        Возвращает False, если коллекция уже существует.

        Args:
            name (CollectionName): Имя коллекции.
            ttl (timedelta): Время жизни коллекции.
            now (datetime): Текущее время.

        Returns:
            bool: Признак создания записи.
        """
        exp = now + ttl
        row = await self._c.fetchrow(
            """
            insert into collections(
                name, created_at, expire_at, sealed_at, status, version
            )
            values ($1, $2, $3, null, 'new', 1)
            on conflict (name) do nothing
            returning name
            """,
            str(name),
            now,
            exp,
        )
        return row is not None

    async def get(self, name: CollectionName) -> CollectionMeta | None:
        """Возвращает метаданные коллекции.

        Args:
            name (CollectionName): Имя коллекции.

        Returns:
            CollectionMeta | None: Метаданные или None.
        """
        row = await self._c.fetchrow(
            """
            select name, created_at, expire_at, sealed_at, status, version
              from collections
             where name = $1
            """,
            str(name),
        )
        if not row:
            return None

        return CollectionMeta(
            name=CollectionName(row["name"]),
            created_at=row["created_at"],
            expire_at=row["expire_at"],
            sealed_at=row["sealed_at"],
            status=row["status"],
            version=row["version"],
        )

    async def seal_uploaded_once(self, name: CollectionName, now: datetime) -> bool:
        """Атомарно помечает первую и единственную загрузку коллекции.

        Args:
            name (CollectionName): Имя коллекции.
            now (datetime): Время запечатки.

        Returns:
            bool: False, если коллекция уже была запечатана.
        """
        row = await self._c.fetchrow(
            """
            update collections
               set sealed_at = $2, status = 'uploaded', version = version + 1
             where name = $1
               and sealed_at is null
            returning name
            """,
            str(name),
            now,
        )
        return row is not None

    async def list_expired(self, now: datetime, limit: int) -> list[CollectionName]:
        """Возвращает имена коллекций, срок жизни которых истёк.

        Args:
            now (datetime): Текущее время.
            limit (int): Максимальное количество имён.

        Returns:
            list[CollectionName]: Отсортированный список по expire_at.
        """
        rows = await self._c.fetch(
            """
            select name
              from collections
             where expire_at <= $1
             order by expire_at asc
             limit $2
            """,
            now,
            limit,
        )
        return [CollectionName(r["name"]) for r in rows]

    async def delete_cascade(self, name: CollectionName) -> None:
        """Удаляет коллекцию и связанные документы.

        Args:
            name (CollectionName): Имя коллекции.
        """
        await self._c.execute(
            "delete from documents where collection = $1",
            str(name),
        )
        await self._c.execute(
            "delete from collections where name = $1",
            str(name),
        )
