"""Адаптер хранилища файлов MinIO S3.

Реализует StoragePort: пакетная загрузка Blob, скачивание, stat, удаление,
очистка по TTL и health-check. Имена объектов обезличены и уникальны.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import Callable, Final, TypeVar

import structlog
from minio import Minio
from minio.error import S3Error
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.domain.exceptions import StorageError
from app.domain.model.shared import (
    Blob,
    ObjectName,
    StoredObject,
    UploadBatch,
    make_object_name,
)
from app.domain.ports import StoragePort
from .models import HeadObject, ObjectMetadata, head_from_stat, mapping_from_meta
from .protocols import MinioLike

__all__ = ["MinioStorage"]

logger = structlog.get_logger(__name__)

_RETRY: Final = {
    "retry": retry_if_exception_type(S3Error),
    "wait": wait_exponential(multiplier=0.1, max=2.0),
    "stop": stop_after_attempt(3),
}

T = TypeVar("T")


@dataclass(slots=True)
class MinioStorage(StoragePort):
    """Адаптер MinIO.

    Attributes:
        endpoint (str): Адрес MinIO (host:port).
        access_key (str): Ключ доступа.
        secret_key (str): Секретный ключ.
        bucket (str): Название бакета.
        secure (bool): Использовать HTTPS.
        client (MinioLike | None): Внедрённый клиент (для тестов).
    """

    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    secure: bool = False
    client: MinioLike | None = None

    def __post_init__(self) -> None:
        """Создаёт клиента, гарантирует наличие бакета и логирует параметры."""
        self._minio: MinioLike = self.client or Minio(
            self.endpoint,
            self.access_key,
            self.secret_key,
            secure=self.secure,
        )
        self._ensure_bucket()

        logger.info(
            "MinioStorage init",
            endpoint=self.endpoint,
            bucket=self.bucket,
            secure=self.secure,
        )

    async def upload(
        self,
        blobs: list[Blob],
        *,
        ttl_minutes: int | None = None,
    ) -> UploadBatch:
        """Загружает объекты в хранилище.

        Args:
            blobs (list[Blob]): Двоичные данные объектов.
            ttl_minutes (int | None): Время жизни объектов в минутах.

        Returns:
            UploadBatch: Имена и метаданные сохранённых объектов.
        """
        logger.debug("upload start", count=len(blobs), ttl=ttl_minutes)

        tasks = [
            self._run(self._put_one, blob, ttl_minutes) for blob in blobs
        ]

        objs = await asyncio.gather(*tasks)
        result = UploadBatch(objects=tuple(objs))

        logger.info("upload done", objects=result.names)

        return result

    async def download(self, object_name: ObjectName) -> Blob:
        """Скачивает объект из хранилища.

        Args:
            object_name (ObjectName): Уникальное имя объекта.

        Returns:
            Blob: Данные, content_type и оригинальное имя (если известно).
        """
        logger.debug("download", object=str(object_name))

        head = await self._run(self._head_sync, object_name)
        data = await self._run(self._get_sync, object_name)

        return Blob(
            data=data,
            content_type=head.content_type,
            filename=head.metadata.original_name,
        )

    async def stat(self, object_name: ObjectName) -> StoredObject:
        """Возвращает метаданные объекта.

        Args:
            object_name (ObjectName): Имя объекта в хранилище.

        Returns:
            StoredObject: Имя, expires_at и оригинальное имя.
        """
        head = await self._run(self._head_sync, object_name)

        return StoredObject(
            name=object_name,
            expires_at=head.metadata.expires_at,
            original_name=head.metadata.original_name,
        )

    async def delete(self, object_name: ObjectName) -> None:
        """Удаляет объект немедленно.

        Args:
            object_name (ObjectName): Имя удаляемого объекта.
        """
        logger.debug("delete", object=str(object_name))

        await self._run(self._remove_sync, object_name)

    async def cleanup_expired(self) -> None:
        """Удаляет объекты, чей TTL истёк."""
        logger.info("cleanup_expired start")

        await self._run(self._cleanup_expired_sync)

        logger.info("cleanup_expired done")

    async def is_healthy(self) -> bool:
        """Проверяет доступность MinIO.

        Returns:
            bool: True, если соединение установлено.
        """
        try:
            await self._run(lambda: self._minio.list_buckets())
            return True
        except S3Error as exc:
            logger.warning("Minio health fail", error=str(exc))
            return False
        except Exception as exc:  # noqa: BLE001
            logger.warning("Minio health exception", error=str(exc))
            return False

    def _ensure_bucket(self) -> None:
        """Создаёт бакет, если он не существует."""
        with self._suppress_s3():
            if not self._minio.bucket_exists(self.bucket):
                self._minio.make_bucket(self.bucket)

                logger.info("bucket created", bucket=self.bucket)

    @retry(**_RETRY)
    def _put_one(self, blob: Blob, ttl_minutes: int | None) -> StoredObject:
        """Загружает один Blob и возвращает StoredObject.

        Args:
            blob (Blob): Данные и метаинформация.
            ttl_minutes (int | None): TTL в минутах.

        Returns:
            StoredObject: Имя, expires_at и оригинальное имя.
        """
        object_name = make_object_name(original_name=blob.filename)
        data = blob.data
        stream = BytesIO(data)
        size = len(data)
        content_type = blob.content_type or "application/octet-stream"
        expires_at = (
            datetime.now(UTC) + timedelta(minutes=ttl_minutes)
            if ttl_minutes
            else None
        )
        meta_dict = mapping_from_meta(
            ObjectMetadata(
                expires_at=expires_at,
                original_name=blob.filename,
                raw={},  # можно прокинуть доп. ключи, если появятся
            )
        )

        self._minio.put_object(
            self.bucket,
            str(object_name),
            stream,
            length=size,
            content_type=content_type,
            metadata=meta_dict or None,
        )

        logger.debug(
            "object uploaded",
            object=str(object_name),
            size=size,
            ttl_minutes=ttl_minutes,
        )

        return StoredObject(
            name=object_name,
            expires_at=expires_at,
            original_name=blob.filename,
        )

    @retry(**_RETRY)
    def _get_sync(self, object_name: ObjectName) -> bytes:
        """Скачивает объект из бакета (синхронно).

        Args:
            object_name (ObjectName): Имя объекта.

        Returns:
            bytes: Содержимое объекта.
        """
        try:
            resp = self._minio.get_object(self.bucket, str(object_name))

            try:
                data = resp.read()

                logger.debug(
                    "object downloaded", object=str(object_name), size=len(data)
                )

                return data
            finally:
                resp.close()
        except S3Error as exc:  # pragma: no cover
            logger.error("download failed", object=str(object_name), error=str(exc))
            raise StorageError(str(exc)) from exc

    @retry(**_RETRY)
    def _head_sync(self, object_name: ObjectName) -> HeadObject:
        """Возвращает нормализованный stat объекта (синхронно).

        Args:
            object_name (ObjectName): Имя объекта.

        Returns:
            HeadObject: Нормализованный набор метаданных объекта.
        """
        stat = self._minio.stat_object(self.bucket, str(object_name))

        return head_from_stat(stat)

    @retry(**_RETRY)
    def _remove_sync(self, object_name: ObjectName) -> None:
        """Удаляет объект из бакета (синхронно).

        Args:
            object_name (ObjectName): Имя объекта.
        """
        with self._suppress_s3():
            self._minio.remove_object(self.bucket, str(object_name))

        logger.debug("object removed", object=str(object_name))

    @retry(**_RETRY)
    def _cleanup_expired_sync(self) -> None:
        """Удаляет объекты с истёкшим TTL (синхронно)."""
        # Локальный импорт, чтобы упростить реорганизации модулей и исключить циклы.
        from .models import meta_from_mapping

        for info in self._minio.list_objects(self.bucket, recursive=True):
            name = info.object_name
            stat = self._minio.stat_object(self.bucket, name)
            meta = stat.metadata or {}
            parsed = meta_from_mapping(meta)
            expires = parsed.expires_at

            if expires and expires <= datetime.now(UTC):
                with self._suppress_s3():
                    self._minio.remove_object(self.bucket, name)

                logger.debug("expired object deleted", object=name)

    async def _run(self, fn: Callable[..., T], *args: object) -> T:
        """Запускает синхронную функцию в thread pool.

        Args:
            fn (Callable[..., T]): Функция.
            *args (object): Аргументы.

        Returns:
            T: Результат вызова функции.
        """
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(None, lambda: fn(*args))

    @contextmanager
    def _suppress_s3(self) -> Iterator[None]:
        """Подавляет ошибки S3Error в критичных местах.

        Returns:
            Iterator[None]: Контекстный итератор, подавляющий S3Error.
        """
        with suppress(S3Error):
            yield
