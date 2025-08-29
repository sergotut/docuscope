"""Настройки для LibreOffice конвертера документов.

Конфигурация конвертера, использующего LibreOffice для преобразования
документов между форматами с управлением пулом процессов.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from app.infrastructure.config.base import SettingsBase

__all__ = [
    "LibreOfficeConverterSettings",
]


class LibreOfficeConverterSettings(SettingsBase):
    """Настройки LibreOffice конвертера документов.

    Специфичные настройки для конвертера LibreOffice.
    Общие параметры берутся из CommonDocumentSettings.

    Attributes:
        min_processes: Минимальное количество процессов в пуле.
        max_processes: Максимальное количество процессов в пуле.
        process_idle_timeout_multiplier: Множитель таймаута простоя
            относительно default_timeout.
        conversion_timeout_multiplier: Множитель таймаута конвертации
            относительно default_timeout.
        libreoffice_path: Путь к исполняемому файлу LibreOffice.
        startup_timeout: Таймаут запуска процесса LibreOffice в секундах.
        max_memory_mb: Максимальное потребление памяти процессом в МБ.
        enable_headless: Запускать ли LibreOffice в headless режиме.
        preserve_metadata: Сохранять ли метаданные при конвертации.
        quality_level: Уровень качества конвертации (1-10).
        enable_process_recycling: Включить ли переработку процессов после N операций.
        max_operations_per_process: Максимальное количество операций на процесс.
        enable_conversion_cache: Включить ли кеширование результатов конвертации.
    """

    min_processes: int = Field(
        2,
        env="CONVERTER_LIBREOFFICE_MIN_PROCESSES",
        ge=1,
        le=50,
        description="Минимальное количество процессов в пуле",
    )

    max_processes: int = Field(
        10,
        env="CONVERTER_LIBREOFFICE_MAX_PROCESSES",
        ge=1,
        le=100,
        description="Максимальное количество процессов в пуле",
    )

    process_idle_timeout_multiplier: float = Field(
        30.0,
        env="CONVERTER_LIBREOFFICE_PROCESS_IDLE_TIMEOUT_MULTIPLIER",
        ge=1.0,
        le=120.0,  # 2 часа при default_timeout=60s
        description="Множитель таймаута простоя процесса относительно default_timeout",
    )

    conversion_timeout_multiplier: float = Field(
        5.0,
        env="CONVERTER_LIBREOFFICE_CONVERSION_TIMEOUT_MULTIPLIER",
        ge=0.5,
        le=60.0,  # 1 час при default_timeout=60s
        description="Множитель таймаута конвертации относительно default_timeout",
    )

    libreoffice_path: str | None = Field(
        None,
        env="CONVERTER_LIBREOFFICE_PATH",
        description="Путь к исполняемому файлу LibreOffice",
    )

    startup_timeout: int = Field(
        60,
        env="CONVERTER_LIBREOFFICE_STARTUP_TIMEOUT",
        ge=10,
        le=300,  # 5 минут max
        description="Таймаут запуска процесса LibreOffice в секундах",
    )

    max_memory_mb: int = Field(
        512,
        env="CONVERTER_LIBREOFFICE_MAX_MEMORY_MB",
        ge=128,
        le=4096,  # 4GB max
        description="Максимальное потребление памяти процессом в МБ",
    )

    enable_headless: bool = Field(
        True,
        env="CONVERTER_LIBREOFFICE_ENABLE_HEADLESS",
        description="Запускать ли LibreOffice в headless режиме",
    )

    preserve_metadata: bool = Field(
        True,
        env="CONVERTER_LIBREOFFICE_PRESERVE_METADATA",
        description="Сохранять ли метаданные при конвертации",
    )

    quality_level: int = Field(
        8,
        env="CONVERTER_LIBREOFFICE_QUALITY_LEVEL",
        ge=1,
        le=10,
        description="Уровень качества конвертации (1-10)",
    )

    enable_process_recycling: bool = Field(
        True,
        env="CONVERTER_LIBREOFFICE_ENABLE_PROCESS_RECYCLING",
        description="Включить ли переработку процессов после N операций",
    )

    max_operations_per_process: int = Field(
        100,
        env="CONVERTER_LIBREOFFICE_MAX_OPERATIONS_PER_PROCESS",
        ge=10,
        le=1000,
        description="Максимальное количество операций на процесс до перезапуска",
    )

    enable_conversion_cache: bool = Field(
        False,
        env="CONVERTER_LIBREOFFICE_ENABLE_CONVERSION_CACHE",
        description="Включить ли кеширование результатов конвертации",
    )

    @field_validator("max_processes")
    @classmethod
    def validate_max_processes(cls, v: int, info) -> int:
        """Валидирует корректность максимального количества процессов.
        
        Проверяет, что максимальное количество процессов в пуле не меньше
        минимального
        
        Args:
            v: Максимальное количество процессов для валидации.
            info: Контекст валидации с доступом к другим полям.
            
        Returns:
            int: Валидированное значение max_processes.
            
        Raises:
            ValueError: Если max_processes меньше min_processes.
        """
        min_processes = info.data.get("min_processes", 1)
        if v < min_processes:
            raise ValueError("max_processes должен быть >= min_processes")
        return v
