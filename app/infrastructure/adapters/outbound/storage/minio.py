"""Shim: реэкспорт адаптера MinioStorage из подпакета minio.

Служит для обратной совместимости.
"""

from .minio_client import MinioStorage

__all__ = ["MinioStorage"]
