"""Конфигурация для LibreOffice адаптера.

Содержит настройки по умолчанию и фабричные методы для создания
адаптера с различными конфигурациями.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "LibreOfficeConfig",
    "create_production_converter",
    "create_development_converter",
]


@dataclass(frozen=True, slots=True)
class LibreOfficeConfig:
    """Конфигурация LibreOffice адаптера.

    Attributes:
        min_processes (int): Минимальное количество процессов в пуле.
        max_processes (int): Максимальное количество процессов.
        process_idle_timeout (int): Таймаут простоя процесса в секундах.
        conversion_timeout (int): Таймаут конвертации в секундах.
        temp_dir (Path | None): Директория для временных файлов.
        cleanup_interval (int): Интервал очистки временных файлов в секундах.
        max_file_size_mb (int): Максимальный размер файла в МБ.
    """

    min_processes: int = 2
    max_processes: int = 10
    process_idle_timeout: int = 1800  # 30 минут
    conversion_timeout: int = 300  # 5 минут
    temp_dir: Path | None = None
    cleanup_interval: int = 3600  # 1 час
    max_file_size_mb: int = 100

    def __post_init__(self) -> None:
        """Валидирует параметры конфигурации."""
        if self.min_processes < 1:
            msg = "min_processes must be >= 1"
            raise ValueError(msg)

        if self.max_processes < self.min_processes:
            msg = "max_processes must be >= min_processes"
            raise ValueError(msg)

        if self.process_idle_timeout < 60:
            msg = "process_idle_timeout must be >= 60 seconds"
            raise ValueError(msg)

        if self.conversion_timeout < 30:
            msg = "conversion_timeout must be >= 30 seconds"
            raise ValueError(msg)

        if self.max_file_size_mb < 1:
            msg = "max_file_size_mb must be >= 1"
            raise ValueError(msg)


def create_production_converter(
    *,
    temp_dir: Path | None = None,
    max_processes: int = 20,
) -> LibreOfficeConfig:
    """Создает конфигурацию для продакшен среды.

    Оптимизировано для высокой нагрузки и надежности.

    Args:
        temp_dir (Path | None): Директория для временных файлов.
        max_processes (int): Максимальное количество процессов.

    Returns:
        LibreOfficeConfig: Конфигурация для продакшена.
    """
    return LibreOfficeConfig(
        min_processes=5,  # Всегда готовые процессы
        max_processes=max_processes,
        process_idle_timeout=1800,  # 30 минут
        conversion_timeout=180,  # 3 минуты (быстрее для продакшена)
        temp_dir=temp_dir,
        cleanup_interval=1800,  # 30 минут
        max_file_size_mb=50,  # Ограничиваем размер для стабильности
    )


def create_development_converter(
    *,
    temp_dir: Path | None = None,
) -> LibreOfficeConfig:
    """Создает конфигурацию для разработки.

    Оптимизировано для быстрого запуска и отладки.

    Args:
        temp_dir (Path | None): Директория для временных файлов.

    Returns:
        LibreOfficeConfig: Конфигурация для разработки.
    """
    return LibreOfficeConfig(
        min_processes=1,  # Минимум для экономии ресурсов
        max_processes=3,
        process_idle_timeout=600,  # 10 минут
        conversion_timeout=60,  # 1 минута
        temp_dir=temp_dir,
        cleanup_interval=300,  # 5 минут
        max_file_size_mb=200,  # Больше лимит для тестирования
    )
