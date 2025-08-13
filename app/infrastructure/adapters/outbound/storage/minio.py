"""Shim: реэкспорт адаптера MinioStorage из подпакета minio.

Служит для обратной совместимости.
"""

from .minio import MinioStorage

__all__ = ["MinioStorage"]
