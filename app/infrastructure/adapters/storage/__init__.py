"""
DI-адаптеры хранилищ файлов.
"""

from .minio import MinIOStorageAdapter
from .null import NullStorage

__all__ = [
    "MinIOStorageAdapter",
    "NullStorage",
]
