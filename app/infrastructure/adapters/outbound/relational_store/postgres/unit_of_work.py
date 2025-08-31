"""Unit of Work для PostgreSQL.

Открывает соединение, начинает транзакцию и предоставляет репозитории.
Гарантирует атомарность операций в рамках одного контекста.
"""

from __future__ import annotations

from typing import AsyncContextManager

from app.domain.ports.relational_store import (
    CollectionRepositoryPort,
    DocumentMetaRepositoryPort,
    RelationalEnginePort,
    RelConnection,
    UnitOfWorkPort,
)

from .repositories import (
    PostgresCollectionRepository,
    PostgresDocumentMetaRepository,
)

__all__ = ["PostgresUnitOfWork"]


class PostgresUnitOfWork(UnitOfWorkPort):
    """UoW с явной транзакцией — обеспечивает ACID на уровне операции.

    Attributes:
        _engine (RelationalEnginePort): Движок реляционной БД.
        _conn (RelConnection | None): Активное соединение.
        _tx_cm (AsyncContextManager[object] | None): Контекст транзакции.
        _acq_cm (AsyncContextManager[RelConnection] | None): Контекст acquire().
        _collections (PostgresCollectionRepository | None): Репозиторий коллекций.
        _documents (PostgresDocumentMetaRepository | None): Репозиторий документов.
    """

    def __init__(self, engine: RelationalEnginePort) -> None:
        """Инициализирует UoW.

        Args:
            engine (RelationalEnginePort): Движок реляционной БД/пула.
        """
        self._engine = engine
        self._conn: RelConnection | None = None
        self._tx_cm: AsyncContextManager[object] | None = None
        self._acq_cm: AsyncContextManager[RelConnection] | None = None
        self._collections: PostgresCollectionRepository | None = None
        self._documents: PostgresDocumentMetaRepository | None = None

    async def __aenter__(self) -> PostgresUnitOfWork:
        """Открывает соединение, начинает транзакцию и готовит репозитории."""
        if not self._engine.is_connected():
            await self._engine.connect()

        self._acq_cm = self._engine.acquire()
        self._conn = await self._acq_cm.__aenter__()
        self._tx_cm = self._conn.transaction()
        await self._tx_cm.__aenter__()

        self._collections = PostgresCollectionRepository(self._conn)
        self._documents = PostgresDocumentMetaRepository(self._conn)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        """Завершает транзакцию и отдаёт соединение в пул."""
        if self._tx_cm is None or self._acq_cm is None:
            raise RuntimeError("UoW.__aexit__ вызван без активного контекста")

        try:
            await self._tx_cm.__aexit__(exc_type, exc, tb)
        finally:
            await self._acq_cm.__aexit__(exc_type, exc, tb)

        self._conn = None
        self._tx_cm = None
        self._acq_cm = None
        self._collections = None
        self._documents = None

    @property
    def collections(self) -> CollectionRepositoryPort:
        """Репозиторий коллекций.

        Returns:
            CollectionRepositoryPort: Репозиторий коллекций.

        Raises:
            RuntimeError: Если UoW ещё не активирован через async with.
        """
        if self._collections is None:
            raise RuntimeError("UoW не инициализирован: collections недоступен")
        return self._collections

    @property
    def documents(self) -> DocumentMetaRepositoryPort:
        """Репозиторий метаданных документов.

        Returns:
            DocumentMetaRepositoryPort: Репозиторий документов.

        Raises:
            RuntimeError: Если UoW ещё не активирован через async with.
        """
        if self._documents is None:
            raise RuntimeError("UoW не инициализирован: documents недоступен")
        return self._documents
