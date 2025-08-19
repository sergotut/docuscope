"""Порт (интерфейс) Unit of Work для реляционного хранилища.

Инкапсулирует транзакцию и доступ к репозиториям через асинхронный
контекстный менеджер.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .collections import CollectionRepositoryPort
from .documents import DocumentMetaRepositoryPort

__all__ = ["UnitOfWorkPort"]


@runtime_checkable
class UnitOfWorkPort(Protocol):
    """Unit of Work (транзакция) поверх реляционного хранилища.

    Использование:
        async with uow:
            ...  # операции через uow.collections / uow.documents
    """

    async def __aenter__(self) -> "UnitOfWorkPort":  # pragma: no cover
        """Открывает транзакцию и возвращает контекст UoW.

        Returns:
            UnitOfWorkPort: Экземпляр UoW в активной транзакции.
        """
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:  # pragma: no cover
        """Завершает транзакцию.

        При отсутствии исключения выполняет commit, иначе rollback.

        Args:
            exc_type (type[BaseException] | None): Тип исключения.
            exc (BaseException | None): Экземпляр исключения.
            tb (object | None): Трассировка стека.
        """
        ...

    @property
    def collections(self) -> CollectionRepositoryPort:
        """Репозиторий коллекций.

        Returns:
            CollectionRepositoryPort: Репозиторий для работы с коллекциями.
        """
        ...

    @property
    def documents(self) -> DocumentMetaRepositoryPort:
        """Репозиторий метаданных документов.

        Returns:
            DocumentMetaRepositoryPort: Репозиторий для метаданных документов.
        """
        ...
