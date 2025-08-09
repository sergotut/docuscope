"""DI-адаптеры хранилиза файлов."""

from .minio import MinioStorageAdapter

__all__ = [
    "MinioStorageAdapter",
]