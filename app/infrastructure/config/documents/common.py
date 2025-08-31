"""Общие настройки для работы с документами."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator

from app.infrastructure.config.base import SettingsBase

__all__ = [
    "CommonDocumentSettings",
]


class CommonDocumentSettings(SettingsBase):
    """Общие настройки для работы с документами.

    Attributes:
        max_document_size_mb: Максимальный размер документа в МБ (1-2048).
        preferred_head_size: Размер буфера для чтения заголовка в байтах (1KB-1MB).
        default_timeout_seconds: Базовый таймаут для операций в секундах (1-600).
        temp_base_dir: Базовая директория для временных файлов (абсолютный путь).
        enable_cleanup: Включить автоматическую очистку временных файлов.
        cleanup_interval_seconds: Интервал очистки временных файлов (5мин-24ч).
        max_concurrent_operations: Лимит параллельных операций (1-100).
        buffer_size_bytes: Размер I/O буфера для файлов в байтах (1KB-64KB).
        enable_metrics: Включить сбор метрик операций с документами.
        quality_threshold: Порог качества для операций в диапазоне 0.0-1.0.
    """

    max_document_size_mb: int = Field(
        200,
        env="DOCUMENTS_MAX_SIZE_MB",
        ge=1,
        le=2048,  # 2GB max
        description="Максимальный размер документа в МБ",
    )

    preferred_head_size: int = Field(
        16384,  # 16KB
        env="DOCUMENTS_PREFERRED_HEAD_SIZE",
        ge=1024,
        le=1048576,  # 1MB max
        description="Размер буфера для чтения заголовка документа в байтах",
    )

    default_timeout_seconds: float = Field(
        60.0,
        env="DOCUMENTS_DEFAULT_TIMEOUT",
        ge=1.0,
        le=600.0,  # 10 minutes max
        description="Таймаут по умолчанию для операций с документами в секундах",
    )

    temp_base_dir: str | None = Field(
        None,
        env="DOCUMENTS_TEMP_BASE_DIR",
        description="Базовая директория для временных файлов",
    )

    enable_cleanup: bool = Field(
        True,
        env="DOCUMENTS_ENABLE_CLEANUP",
        description="Включить ли автоматическую очистку временных файлов",
    )

    cleanup_interval_seconds: int = Field(
        3600,  # 1 час
        env="DOCUMENTS_CLEANUP_INTERVAL",
        ge=300,  # 5 минут min
        le=86400,  # 24 часа max
        description="Интервал очистки временных файлов в секундах",
    )

    max_concurrent_operations: int = Field(
        10,
        env="DOCUMENTS_MAX_CONCURRENT_OPERATIONS",
        ge=1,
        le=100,
        description="Максимальное количество параллельных операций с документами",
    )

    buffer_size_bytes: int = Field(
        8192,  # 8KB
        env="DOCUMENTS_BUFFER_SIZE",
        ge=1024,  # 1KB min
        le=65536,  # 64KB max
        description="Размер буфера для чтения/записи файлов в байтах",
    )

    enable_metrics: bool = Field(
        True,
        env="DOCUMENTS_ENABLE_METRICS",
        description="Включить ли сбор метрик операций с документами",
    )

    quality_threshold: float = Field(
        0.7,
        env="DOCUMENTS_QUALITY_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="Порог качества для операций с документами (0.0-1.0)",
    )

    max_filename_length: int = Field(
        255,
        env="DOCUMENTS_MAX_FILENAME_LENGTH",
        ge=1,
        le=4096,
        description="Максимальная длина имени файла",
    )

    @field_validator("temp_base_dir")
    @classmethod
    def validate_temp_base_dir(cls, v: str | None) -> str | None:
        """Валидирует путь к базовой временной директории.

        Проверяет, что указанный путь является абсолютным, если он задан.
        None значение разрешено и означает использование системной временной
        директории по умолчанию.

        Args:
            v: Путь к временной директории или None.

        Returns:
            str | None: Валидированный путь к временной директории или None.

        Raises:
            ValueError: Если путь не является абсолютным.
        """
        if v is None:
            return v

        path = Path(v)
        if not path.is_absolute():
            raise ValueError("temp_base_dir должен быть абсолютным путём")

        return v

    @property
    def max_document_size_bytes(self) -> int:
        """Возвращает максимальный размер документа в байтах.

        Конвертирует значение max_document_size_mb в байты для удобного
        использования в коде, который работает с размерами файлов в байтах.

        Returns:
            int: Максимальный размер документа в байтах.
        """
        return self.max_document_size_mb * 1024 * 1024

    @property
    def temp_base_path(self) -> Path | None:
        """Возвращает Path объект для базовой временной директории.

        Преобразует строковое значение temp_base_dir в объект Path для
        удобного использования в коде, который работает с файловой системой.

        Returns:
            Path | None: Объект для базовой временной директории или None если
                директория не задана.
        """
        return Path(self.temp_base_dir) if self.temp_base_dir else None
