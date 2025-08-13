"""Протоколы для типизации клиента MinIO и связанных объектов.

Минимальные интерфейсы, чтобы не зависеть жёстко от SDK.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from io import BytesIO
from typing import Protocol, runtime_checkable

__all__ = ["Readable", "StatResult", "ObjectInfo", "MinioLike"]


@runtime_checkable
class Readable(Protocol):
    """Потоковый ответ get_object с методами read и close."""

    def read(self, amt: int | None = None) -> bytes:
        """Читает содержимое потока.

        Args:
            amt (int | None): Максимальное количество байт. Если None, будет
                прочитано всё доступное содержимое.

        Returns:
            bytes: Прочитанные байты.
        """
        ...

    def close(self) -> None:
        """Закрывает поток."""
        ...


@runtime_checkable
class StatResult(Protocol):
    """Результат операции stat_object.

    Attributes:
        content_type (str | None): MIME-тип объекта.
        metadata (dict[str, str] | None): Пользовательские метаданные.
        size (int | None): Размер в байтах.
        etag (str | None): ETag объекта.
        last_modified (datetime | None): Дата последнего изменения.
        version_id (str | None): Идентификатор версии объекта.
        storage_class (str | None): Класс хранения.
    """

    @property
    def content_type(self) -> str | None:
        """MIME-тип объекта.

        Returns:
            str | None: Значение заголовка Content-Type.
        """
        ...

    @property
    def metadata(self) -> dict[str, str] | None:
        """Пользовательские метаданные.

        Returns:
            dict[str, str] | None: Пары ключ-значение метаданных.
        """
        ...

    # Необязательные поля (могут отсутствовать у разных клиентов)
    @property
    def size(self) -> int | None:
        """Размер объекта в байтах.

        Returns:
            int | None: Размер, если доступен.
        """
        ...

    @property
    def etag(self) -> str | None:
        """ETag объекта.

        Returns:
            str | None: Значение ETag.
        """
        ...

    @property
    def last_modified(self) -> datetime | None:
        """Момент последнего изменения.

        Returns:
            datetime | None: Дата и время в UTC.
        """
        ...

    @property
    def version_id(self) -> str | None:
        """Идентификатор версии объекта.

        Returns:
            str | None: Версия, если версионирование включено.
        """
        ...

    @property
    def storage_class(self) -> str | None:
        """Класс хранения.

        Returns:
            str | None: Класс хранения (например, STANDARD).
        """
        ...


@runtime_checkable
class ObjectInfo(Protocol):
    """Элемент, возвращаемый list_objects.

    Attributes:
        object_name (str): Имя объекта.
        size (int | None): Размер в байтах.
        etag (str | None): ETag объекта.
        last_modified (datetime | None): Дата последнего изменения.
        version_id (str | None): Идентификатор версии.
        is_dir (bool | None): Признак псевдокаталога.
    """

    @property
    def object_name(self) -> str:
        """Имя объекта.

        Returns:
            str: Полное имя (ключ) объекта в бакете.
        """
        ...

    # Необязательные поля
    @property
    def size(self) -> int | None:
        """Размер объекта в байтах.

        Returns:
            int | None: Размер, если доступен.
        """
        ...

    @property
    def etag(self) -> str | None:
        """ETag объекта.

        Returns:
            str | None: Значение ETag.
        """
        ...

    @property
    def last_modified(self) -> datetime | None:
        """Момент последнего изменения.

        Returns:
            datetime | None: Дата и время в UTC.
        """
        ...

    @property
    def version_id(self) -> str | None:
        """Идентификатор версии объекта.

        Returns:
            str | None: Версия, если версионирование включено.
        """
        ...

    @property
    def is_dir(self) -> bool | None:
        """Признак псевдокаталога.

        Returns:
            bool | None: True, если элемент представляет каталог.
        """
        ...


@runtime_checkable
class MinioLike(Protocol):
    """Минимальный интерфейс клиента MinIO, используемый адаптером."""

    def list_buckets(self) -> list[object]:
        """Возвращает список доступных бакетов.

        Returns:
            list[object]: Коллекция дескрипторов бакетов.
        """
        ...

    def bucket_exists(self, bucket_name: str) -> bool:
        """Проверяет существование бакета.

        Args:
            bucket_name (str): Имя бакета.

        Returns:
            bool: True, если бакет существует.
        """
        ...

    def make_bucket(self, bucket_name: str) -> None:
        """Создаёт новый бакет.

        Args:
            bucket_name (str): Имя создаваемого бакета.
        """
        ...

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: BytesIO,
        length: int,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> object:
        """Загружает объект в бакет.

        Args:
            bucket_name (str): Имя бакета.
            object_name (str): Ключ объекта.
            data (BytesIO): Поток байтов с данными.
            length (int): Длина данных в байтах.
            content_type (str | None): MIME-тип содержимого.
            metadata (dict[str, str] | None): Пользовательские метаданные.

        Returns:
            object: Результат, возвращаемый клиентом.
        """
        ...

    def get_object(self, bucket_name: str, object_name: str) -> Readable:
        """Возвращает поток для чтения объекта.

        Args:
            bucket_name (str): Имя бакета.
            object_name (str): Ключ объекта.

        Returns:
            Readable: Потоковый объект для чтения данных.
        """
        ...

    def stat_object(self, bucket_name: str, object_name: str) -> StatResult:
        """Возвращает метаданные объекта.

        Args:
            bucket_name (str): Имя бакета.
            object_name (str): Ключ объекта.

        Returns:
            StatResult: Метаданные и свойства объекта.
        """
        ...

    def remove_object(self, bucket_name: str, object_name: str) -> None:
        """Удаляет объект.

        Args:
            bucket_name (str): Имя бакета.
            object_name (str): Ключ объекта.
        """
        ...

    def list_objects(
        self,
        bucket_name: str,
        recursive: bool = False,
    ) -> Iterable[ObjectInfo]:
        """Итерирует объекты в бакете.

        Args:
            bucket_name (str): Имя бакета.
            recursive (bool): Если True, обход с рекурсией по префиксам.

        Returns:
            Iterable[ObjectInfo]: Итератор по найденным объектам.
        """
        ...
