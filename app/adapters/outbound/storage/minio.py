"""Адаптер хранилища файлов MinIO S3.

Реализует протокол StoragePort.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
from contextlib import contextmanager, suppress
from io import BytesIO
from pathlib import Path
from typing import IO, Final
from uuid import uuid4

import structlog
from minio import Minio
from minio.error import S3Error
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.exceptions import StorageError
from app.core.ports.storage import StoragePort

logger = structlog.get_logger(__name__)

_META_TTL_KEY = "expires_at"
_RETRY: Final = dict(
    retry=retry_if_exception_type(S3Error),
    wait=wait_exponential(multiplier=0.1, max=2.0),
    stop=stop_after_attempt(3),
)


class MinioStorage(StoragePort):
    """Адаптер MinIO."""

    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        client: Minio | None = None,
    ) -> None:
        """Инициализация адаптера Minio.

        Args:
            endpoint (str): Адрес MinIO (host:port).
            access_key (str): Ключ доступа.
            secret_key (str): Секретный ключ.
            bucket (str): Название бакета.
            client (Minio | None): Кастомный клиент (опционально).
        """
        self._bucket = bucket
        self._minio = client or Minio(
            endpoint,
            access_key,
            secret_key,
            secure=endpoint.startswith("https"),
        )
        self._ensure_bucket()
        logger.info(
            "MinioStorage init",
            endpoint=endpoint,
            bucket=bucket,
            secure=endpoint.startswith("https"),
        )

    async def upload(
        self,
        files: list[Path | IO[bytes]],
        *,
        ttl_minutes: int | None = None,
    ) -> list[str]:
        """Загружает список файлов и возвращает object_name каждого.

        Args:
            files (list[Path | IO[bytes]]): Список файлов или потоков.
            ttl_minutes (int | None): Время жизни объекта в минутах.

        Returns:
            list[str]: Имена объектов в бакете.
        """
        logger.debug("upload start", cnt=len(files), ttl=ttl_minutes)
        tasks = [
            self._run(self._put_object, src, ttl_minutes)
            for src in files
        ]
        result = await asyncio.gather(*tasks)
        logger.info("upload done", objects=result)
        return result

    async def download(
        self,
        object_name: str
    ) -> bytes:
        """Скачивает объект по имени.

        Args:
            object_name (str): Имя объекта в бакете.

        Returns:
            bytes: Содержимое файла.
        """
        logger.debug("download", object=object_name)
        return await self._run(self._get, object_name)

    async def delete(
        self,
        object_name: str
    ) -> None:
        """Удаляет объект по имени.

        Args:
            object_name (str): Имя объекта.
        """
        logger.debug("delete", object=object_name)
        await self._run(self._remove, object_name)

    async def cleanup_expired(self) -> None:
        """Удаляет устаревшие объекты с истёкшим TTL."""
        logger.info("cleanup_expired start")
        await self._run(self._cleanup_expired_sync)
        logger.info("cleanup_expired done")

    def is_healthy(self) -> bool:  # noqa: D401
        """Проверяет доступность MinIO.

        Returns:
            bool: True, если соединение установлено.
        """
        try:
            self._minio.list_buckets()
            return True
        except S3Error as exc:
            logger.warning("minio health fail", error=str(exc))
            return False

    def _ensure_bucket(self) -> None:
        """Создаёт бакет, если он не существует."""
        with self._suppress_s3():
            if not self._minio.bucket_exists(self._bucket):
                self._minio.make_bucket(self._bucket)
                logger.info("bucket created", bucket=self._bucket)

    @retry(**_RETRY)
    def _put_object(
        self,
        src: Path | IO[bytes],
        ttl_minutes: int | None,
    ) -> str:
        """Загружает один файл или поток.

        Args:
            src (Path | IO[bytes]): Источник — файл или поток.
            ttl_minutes (int | None): TTL в минутах.

        Returns:
            str: Имя загруженного объекта.
        """
        if isinstance(src, Path):
            stream = src.open("rb")
            size = src.stat().st_size
            object_name = src.name
        else:
            data = src.read()
            stream = BytesIO(data)
            size = len(data)
            object_name = f"upload-{uuid4().hex}"

        metadata = self._make_expiry_meta(ttl_minutes)

        self._minio.put_object(
            self._bucket,
            object_name,
            stream,
            length=size,
            metadata=metadata,
        )
        logger.debug("object uploaded", object=object_name, size=size, ttl=ttl_minutes)
        return object_name

    @retry(**_RETRY)
    def _get(
        self,
        obj: str
    ) -> bytes:
        """Скачивает объект из бакета.

        Args:
            obj (str): Имя объекта.

        Returns:
            bytes: Содержимое объекта.
        """
        try:
            resp = self._minio.get_object(self._bucket, obj)
            with resp as s:
                data = s.read()
                logger.debug("object downloaded", object=obj, size=len(data))
                return data
        except S3Error as exc:
            logger.error("download failed", object=obj, error=str(exc))
            raise StorageError(str(exc)) from exc

    @retry(**_RETRY)
    def _remove(
        self,
        obj: str
    ) -> None:
        """Удаляет объект из бакета.

        Args:
            obj (str): Имя объекта.
        """
        self._minio.remove_object(self._bucket, obj)
        logger.debug("object removed", object=obj)

    def _cleanup_expired_sync(self) -> None:
        """Удаляет все объекты, чей TTL истёк."""
        now = _dt.datetime.utcnow()
        for obj in self._minio.list_objects(self._bucket, recursive=True):
            meta = self._minio.stat_object(self._bucket, obj.object_name).metadata
            expires_at = meta.get(_META_TTL_KEY) if meta else None
            if expires_at and _dt.datetime.fromisoformat(expires_at) < now:
                self._minio.remove_object(self._bucket, obj.object_name)
                logger.debug("expired object deleted", object=obj.object_name)

    async def _run(self, fn, *args):
        """Асинхронно запускает синхронную функцию в thread pool.

        Args:
            fn (Callable): Функция.
            *args: Аргументы.

        Returns:
            Any: Результат функции.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fn, *args)

    def _make_expiry_meta(
        self,
        ttl_minutes: int | None
    ) -> dict[str, str] | None:
        """Формирует объектную метаинформацию с TTL.

        Args:
            ttl_minutes (int | None): Время жизни объекта.

        Returns:
            dict[str, str] | None: Метаданные с ключом expires_at.
        """
        if not ttl_minutes:
            return None
        expires = (_dt.datetime.utcnow() + _dt.timedelta(minutes=ttl_minutes)).isoformat()
        return {_META_TTL_KEY: expires}

    @contextmanager
    def _suppress_s3(self):
        """Контекст, подавляющий ошибки S3Error."""
        with suppress(S3Error):
            yield
