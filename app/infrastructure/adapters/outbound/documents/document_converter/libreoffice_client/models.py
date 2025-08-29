"""Внутренние модели для LibreOffice адаптера.

Содержит value objects и enums для инкапсуляции инфраструктурных деталей
LibreOffice, изолируя их от доменных моделей.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

__all__ = [
    "ProcessState",
    "ConversionCommand",
    "ProcessInfo",
    "ConversionMetrics",
    "LibreOfficeFormat",
    "DOMAIN_TO_LIBREOFFICE_FORMAT",
]


class ProcessState(str, Enum):
    """Состояние LibreOffice процесса."""

    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    STOPPING = "stopping"
    FAILED = "failed"


class LibreOfficeFormat(str, Enum):
    """Поддерживаемые форматы LibreOffice."""

    DOC = "doc"
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"


@dataclass(frozen=True, slots=True)
class ConversionCommand:
    """Команда конвертации для LibreOffice процесса.

    Attributes:
        input_path (Path): Путь к исходному файлу.
        output_dir (Path): Директория для сохранения результата.
        target_format (LibreOfficeFormat): Целевой формат конвертации.
        timeout_seconds (int): Таймаут операции в секундах.
    """

    input_path: Path
    output_dir: Path
    target_format: LibreOfficeFormat
    timeout_seconds: int = 300  # 5 минут по умолчанию


@dataclass(slots=True)
class ProcessInfo:
    """Информация о LibreOffice процессе.

    Attributes:
        pid (int | None): Process ID или None если не запущен.
        state (ProcessState): Текущее состояние процесса.
        started_at (float): Время запуска (time.time()).
        last_used_at (float): Время последнего использования.
        conversions_count (int): Количество выполненных конвертаций.
        failures_count (int): Количество неудачных операций.
    """

    pid: int | None = None
    state: ProcessState = ProcessState.STARTING
    started_at: float = 0.0
    last_used_at: float = 0.0
    conversions_count: int = 0
    failures_count: int = 0

    def __post_init__(self) -> None:
        """Инициализирует временные метки."""
        if self.started_at == 0.0:
            self.started_at = time.time()
        if self.last_used_at == 0.0:
            self.last_used_at = self.started_at

    @property
    def uptime_seconds(self) -> float:
        """Время работы процесса в секундах."""
        return time.time() - self.started_at

    @property
    def idle_seconds(self) -> float:
        """Время простоя процесса в секундах."""
        return time.time() - self.last_used_at

    @property
    def success_rate(self) -> float:
        """Процент успешных конвертаций (0.0-1.0)."""
        total = self.conversions_count + self.failures_count
        return self.conversions_count / total if total > 0 else 1.0

    def mark_used(self) -> None:
        """Отмечает процесс как использованный."""
        self.last_used_at = time.time()
        self.conversions_count += 1

    def mark_failed(self) -> None:
        """Отмечает неудачную операцию."""
        self.last_used_at = time.time()
        self.failures_count += 1


@dataclass(slots=True)
class ConversionMetrics:
    """Метрики производительности конвертации.

    Attributes:
        total_conversions (int): Общее количество конвертаций.
        successful_conversions (int): Успешные конвертации.
        failed_conversions (int): Неудачные конвертации.
        total_time_ms (float): Общее время конвертаций в миллисекундах.
        queue_wait_time_ms (float): Время ожидания в очереди в миллисекундах.
        active_processes (int): Количество активных процессов.
        queue_size (int): Размер очереди задач.
    """

    total_conversions: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    total_time_ms: float = 0.0
    queue_wait_time_ms: float = 0.0
    active_processes: int = 0
    queue_size: int = 0

    @property
    def success_rate(self) -> float:
        """Процент успешных конвертаций (0.0-1.0)."""
        return (
            self.successful_conversions / self.total_conversions
            if self.total_conversions > 0
            else 0.0
        )

    @property
    def average_conversion_time_ms(self) -> float:
        """Среднее время конвертации в миллисекундах."""
        return (
            self.total_time_ms / self.successful_conversions
            if self.successful_conversions > 0
            else 0.0
        )

    @property
    def average_queue_wait_time_ms(self) -> float:
        """Среднее время ожидания в очереди в миллисекундах."""
        return (
            self.queue_wait_time_ms / self.total_conversions
            if self.total_conversions > 0
            else 0.0
        )


# Константы для LibreOffice
LIBREOFFICE_STARTUP_TIMEOUT: Final[int] = 30  # секунд
LIBREOFFICE_CONVERSION_TIMEOUT: Final[int] = 300  # секунд
LIBREOFFICE_IDLE_TIMEOUT: Final[int] = 1800  # 30 минут
LIBREOFFICE_MAX_FAILURES: Final[int] = 3  # максимум неудач перед перезапуском

# Соответствие доменных типов и LibreOffice форматов
DOMAIN_TO_LIBREOFFICE_FORMAT: Final[dict[tuple[str, str], LibreOfficeFormat]] = {
    ("word_doc", "word_docx"): LibreOfficeFormat.DOCX,
    ("excel_xls", "excel_xlsx"): LibreOfficeFormat.XLSX,
}
