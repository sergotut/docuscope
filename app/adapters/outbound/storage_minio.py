"""
Модуль для интеграции с объектным хранилищем MinIO.

Позволяет загружать и скачивать файлы (например, документы пользователей).
"""

import structlog
from minio import Minio

logger = structlog.get_logger()


class MinIOStorage:
    """ Адаптер для работы с хранилищем файлов MinIO. """
    
    def __init__(self, endpoint, access_key, secret_key):
        """
        Инициализация клиента MinIO и создание бакета для хранения документов.

        Args:
            endpoint (str): Адрес MinIO-сервера (URL).
            access_key (str): Access key для MinIO.
            secret_key (str): Secret key для MinIO.
        """
        self.client = Minio(
            endpoint.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=endpoint.startswith("https://"),
        )
        self.bucket = "documents"
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        logger.info("minio_ready", bucket=self.bucket, endpoint=endpoint)

    def upload(self, file_bytes: bytes, filename: str) -> str:
        """
        Загружает файл в MinIO.

        Args:
            file_bytes (bytes): Содержимое файла в байтах.
            filename (str): Имя файла (уникальное в бакете).

        Returns:
            str: Строка с путем к файлу в формате 'bucket/filename'.
        """
        self.client.put_object(
            self.bucket,
            filename,
            data=bytes(file_bytes),
            length=len(file_bytes),
        )
        logger.info("file_uploaded", filename=filename, size=len(file_bytes))
        return f"{self.bucket}/{filename}"

    def download(self, filename: str) -> bytes:
        """
        Скачивает файл из MinIO по имени.

        Args:
            filename (str): Имя файла для скачивания.

        Returns:
            bytes: Содержимое файла в виде байтов.
        """
        resp = self.client.get_object(self.bucket, filename)
        logger.info("file_downloaded", filename=filename)
        return resp.read()
