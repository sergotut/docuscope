"""LibreOffice адаптер для высокопроизводительной конвертации документов.

Реализует DocumentConverterPort с использованием LibreOffice в headless режиме.
Оптимизирован для обработки тысяч документов с минимальными задержками.
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path

import structlog

from app.domain.exceptions import DocumentConversionError, DomainValidationError
from app.domain.model.diagnostics import DocumentConverterHealthReport
from app.domain.model.documents.conversion import (
    SUPPORTED_CONVERSIONS,
    ConversionRequest,
    ConversionResult,
)
from app.domain.model.documents.types import DocumentType
from app.domain.model.documents.warnings import (
    WARN_CONVERSION_FEATURES_UNSUPPORTED,
    WARN_CONVERSION_QUALITY_LOSS,
)
from app.domain.ports import DocumentConverterPort

from ..libreoffice_client import (
    DOMAIN_TO_LIBREOFFICE_FORMAT,
    ConversionCommand,
    LibreOfficeFormat,
    LibreOfficeProcessManager,
)

__all__ = ["LibreOfficeDocumentConverter"]

logger = structlog.get_logger(__name__)


class LibreOfficeDocumentConverter(DocumentConverterPort):
    """Высокопроизводительный LibreOffice адаптер для конвертации документов.

    Особенности:
    - Process pooling для параллельной обработки
    - Автоматическое управление временными файлами
    - Мониторинг производительности и health-check
    - Graceful shutdown и error recovery
    - Оптимизация для высокой нагрузки (тысячи пользователей)

    Attributes:
        min_processes (int): Минимальное количество LibreOffice процессов.
        max_processes (int): Максимальное количество процессов.
        process_idle_timeout (int): Таймаут простоя процесса в секундах.
        temp_dir (Path | None): Директория для временных файлов.
        conversion_timeout (int): Таймаут конвертации в секундах.
    """

    def __init__(
        self,
        *,
        min_processes: int = 2,
        max_processes: int = 10,
        process_idle_timeout: int = 1800,  # 30 минут
        temp_dir: Path | None = None,
        conversion_timeout: int = 300,  # 5 минут
    ) -> None:
        """Инициализирует LibreOffice адаптер.

        Args:
            min_processes (int): Минимальное количество процессов в пуле.
            max_processes (int): Максимальное количество процессов.
            process_idle_timeout (int): Таймаут простоя процесса в секундах.
            temp_dir (Path | None): Директория для временных файлов.
            conversion_timeout (int): Таймаут конвертации в секундах.
        """
        self._min_processes = min_processes
        self._max_processes = max_processes
        self._conversion_timeout = conversion_timeout
        self._temp_dir = temp_dir or Path(tempfile.gettempdir()) / "docuscope_converter"
        self._start_time = time.time()

        # Менеджер процессов
        self._process_manager = LibreOfficeProcessManager(
            min_processes=min_processes,
            max_processes=max_processes,
            process_idle_timeout=process_idle_timeout,
            temp_dir=self._temp_dir,
        )

        # Состояние адаптера
        self._is_started = False
        self._startup_lock = asyncio.Lock()

        logger.info(
            "LibreOffice document converter initialized",
            min_processes=min_processes,
            max_processes=max_processes,
            temp_dir=str(self._temp_dir),
        )

    async def convert(self, request: ConversionRequest) -> ConversionResult:
        """Выполняет конвертацию документа согласно запросу.

        Args:
            request (ConversionRequest): Запрос на конвертацию с исходными
                данными документа и целевым типом.

        Returns:
            ConversionResult: Результат конвертации с новыми данными документа,
                статусом операции и возможными предупреждениями о потере качества
                или неподдерживаемых функциях.

        Raises:
            DomainValidationError: Если запрос некорректен (неподдерживаемые
                типы конвертации, пустые данные документа).
            DocumentConversionError: При технических ошибках конвертации
                (повреждённый файл, недоступность конвертера, ошибки I/O).
        """
        # Валидируем запрос
        self._validate_conversion_request(request)

        # Обеспечиваем запуск менеджера процессов
        await self._ensure_started()

        start_time = time.time()
        temp_input_file: Path | None = None
        temp_output_dir: Path | None = None

        try:
            # Создаем временные файлы
            temp_input_file, temp_output_dir = await self._create_temp_files(request)

            # Определяем целевой формат LibreOffice
            target_format = self._get_libreoffice_format(
                request.from_type, request.to_type
            )

            # Создаем команду конвертации
            command = ConversionCommand(
                input_path=temp_input_file,
                output_dir=temp_output_dir,
                target_format=target_format,
                timeout_seconds=self._conversion_timeout,
            )

            # Выполняем конвертацию
            result_path = await self._process_manager.convert(command)

            # Читаем результат
            converted_data = await self._read_converted_file(result_path)

            # Определяем предупреждения
            warnings = self._analyze_conversion_warnings(request, converted_data)

            # Вычисляем время конвертации
            conversion_time_ms = (time.time() - start_time) * 1000

            logger.info(
                "Document conversion completed",
                document_id=request.document_id,
                from_type=request.from_type.value,
                to_type=request.to_type.value,
                size_bytes=len(converted_data),
                conversion_time_ms=conversion_time_ms,
                warnings_count=len(warnings),
            )

            return ConversionResult.success(
                document_id=request.document_id,
                converted_data=converted_data,
                target_type=request.to_type,
                warnings=warnings,
            )

        except DocumentConversionError:
            # Логируем и перебрасываем доменные ошибки
            conversion_time_ms = (time.time() - start_time) * 1000
            logger.error(
                "Document conversion failed",
                document_id=request.document_id,
                from_type=request.from_type.value,
                to_type=request.to_type.value,
                conversion_time_ms=conversion_time_ms,
                exc_info=True,
            )
            raise

        except Exception as exc:
            # Оборачиваем неожиданные ошибки
            conversion_time_ms = (time.time() - start_time) * 1000
            logger.error(
                "Unexpected error during conversion",
                document_id=request.document_id,
                error=str(exc),
                conversion_time_ms=conversion_time_ms,
                exc_info=True,
            )

            return ConversionResult.failure(
                document_id=request.document_id,
                target_type=request.to_type,
                error_message=f"Unexpected conversion error: {exc}",
            )

        finally:
            # Очищаем временные файлы
            await self._cleanup_temp_files(temp_input_file, temp_output_dir)

    def is_conversion_supported(
        self,
        from_type: DocumentType,
        to_type: DocumentType,
    ) -> bool:
        """Проверяет поддержку конвертации между указанными типами.

        Args:
            from_type (DocumentType): Исходный тип документа.
            to_type (DocumentType): Целевой тип документа.

        Returns:
            bool: True, если конвертация поддерживается, иначе False.
        """
        return (from_type, to_type) in SUPPORTED_CONVERSIONS

    @property
    def supported_conversions(self) -> frozenset[tuple[DocumentType, DocumentType]]:
        """Возвращает множество поддерживаемых пар конвертации.

        Returns:
            frozenset[tuple[DocumentType, DocumentType]]: Неизменяемое множество
                кортежей (исходный_тип, целевой_тип) для всех поддерживаемых
                конвертаций.
        """
        return SUPPORTED_CONVERSIONS

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если сервис конвертации доступен и готов к работе.
        """
        try:
            await self._ensure_started()

            # Проверяем доступность LibreOffice
            process = await asyncio.create_subprocess_exec(
                "libreoffice",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)

            if process.returncode != 0:
                logger.warning(
                    "LibreOffice health check failed",
                    returncode=process.returncode,
                    stderr=stderr.decode("utf-8", errors="ignore") if stderr else None,
                )
                return False

            # Проверяем метрики процессов
            metrics = await self._process_manager.get_metrics()

            # Считаем здоровым, если есть активные процессы и success rate > 80%
            return metrics.active_processes > 0 and (
                metrics.success_rate > 0.8 or metrics.total_conversions < 10
            )

        except Exception as exc:
            logger.error("Health check failed", error=str(exc))
            return False

    async def health(self) -> DocumentConverterHealthReport:
        """Подробный health-репорт.

        Returns:
            DocumentConverterHealthReport: Метаинформация о состоянии конвертера,
                включая статистику конвертаций, производительность и доступность
                внешних инструментов.
        """
        try:
            # Получаем версию LibreOffice
            version = await self._get_libreoffice_version()

            # Получаем метрики
            metrics = await self._process_manager.get_metrics()

            # Определяем статус
            if metrics.active_processes == 0:
                status = "unavailable"
            elif metrics.success_rate < 0.8 and metrics.total_conversions >= 10:
                status = "degraded"
            else:
                status = "healthy"

            return DocumentConverterHealthReport(
                engine="libreoffice",
                version=version,
                status=status,
                supported_formats=[
                    f"{from_type.value}->{to_type.value}"
                    for from_type, to_type in SUPPORTED_CONVERSIONS
                ],
                concurrent_conversions=max(
                    0, metrics.active_processes - metrics.queue_size
                ),
                max_concurrent_conversions=self._max_processes,
                total_conversions=metrics.total_conversions,
                successful_conversions=metrics.successful_conversions,
                failed_conversions=metrics.failed_conversions,
                average_conversion_time_ms=metrics.average_conversion_time_ms,
                queue_size=metrics.queue_size,
                temp_dir_size_bytes=await self._get_temp_dir_size(),
                uptime_seconds=int(time.time() - self._start_time),
                last_conversion_timestamp=int(time.time()),  # Приблизительно
            )

        except Exception as exc:
            logger.error("Failed to generate health report", error=str(exc))

            return DocumentConverterHealthReport(
                engine="libreoffice",
                version="unknown",
                status="failed",
                supported_formats=[],
                concurrent_conversions=0,
                max_concurrent_conversions=self._max_processes,
                total_conversions=0,
                successful_conversions=0,
                failed_conversions=0,
                average_conversion_time_ms=0.0,
                queue_size=0,
                temp_dir_size_bytes=0,
                uptime_seconds=int(time.time() - self._start_time),
                last_conversion_timestamp=0,
            )

    @property
    def max_concurrent_conversions(self) -> int:
        """Максимальное количество параллельных конвертаций.

        Returns:
            int: Лимит одновременно выполняемых операций конвертации.
        """
        return self._max_processes

    async def start(self) -> None:
        """Запускает адаптер и менеджер процессов."""
        async with self._startup_lock:
            if self._is_started:
                return

            await self._process_manager.start()
            self._is_started = True

            logger.info("LibreOffice document converter started")

    async def stop(self) -> None:
        """Останавливает адаптер и менеджер процессов."""
        async with self._startup_lock:
            if not self._is_started:
                return

            await self._process_manager.stop()
            self._is_started = False

            logger.info("LibreOffice document converter stopped")

    # Приватные методы

    async def _ensure_started(self) -> None:
        """Обеспечивает запуск адаптера."""
        if not self._is_started:
            await self.start()

    def _validate_conversion_request(self, request: ConversionRequest) -> None:
        """Валидирует запрос на конвертацию."""
        if not self.is_conversion_supported(request.from_type, request.to_type):
            raise DomainValidationError(
                f"Conversion {request.from_type.value} -> {request.to_type.value} "
                f"is not supported by LibreOffice adapter"
            )

        if not request.source_data:
            raise DomainValidationError("Source data cannot be empty")

        # Проверяем размер файла (защита от слишком больших файлов)
        max_size_mb = 100  # 100MB
        if len(request.source_data) > max_size_mb * 1024 * 1024:
            raise DomainValidationError(
                f"Source file too large: {len(request.source_data)} bytes "
                f"(max {max_size_mb}MB)"
            )

    def _get_libreoffice_format(
        self,
        from_type: DocumentType,
        to_type: DocumentType,
    ) -> LibreOfficeFormat:
        """Определяет целевой формат LibreOffice."""
        format_key = (from_type.value, to_type.value)

        if format_key not in DOMAIN_TO_LIBREOFFICE_FORMAT:
            raise DomainValidationError(
                f"No LibreOffice format mapping for {from_type.value}->{to_type.value}"
            )

        return DOMAIN_TO_LIBREOFFICE_FORMAT[format_key]

    async def _create_temp_files(
        self,
        request: ConversionRequest,
    ) -> tuple[Path, Path]:
        """Создает временные файлы для конвертации."""
        # Создаем уникальную директорию для операции
        operation_id = f"{request.document_id}_{int(time.time() * 1000000)}"
        temp_operation_dir = self._temp_dir / operation_id
        temp_operation_dir.mkdir(parents=True, exist_ok=True)

        # Определяем расширение исходного файла
        source_extension = self._get_source_extension(request.from_type)

        # Создаем временный входной файл
        temp_input_file = temp_operation_dir / f"input{source_extension}"
        temp_input_file.write_bytes(request.source_data)

        # Создаем директорию для выходного файла
        temp_output_dir = temp_operation_dir / "output"
        temp_output_dir.mkdir(exist_ok=True)

        return temp_input_file, temp_output_dir

    def _get_source_extension(self, document_type: DocumentType) -> str:
        """Возвращает расширение файла для типа документа."""
        extension_map = {
            DocumentType.WORD_DOC: ".doc",
            DocumentType.EXCEL_XLS: ".xls",
        }

        return extension_map.get(document_type, ".tmp")

    async def _read_converted_file(self, result_path: Path) -> bytes:
        """Читает сконвертированный файл."""
        if not result_path.exists():
            raise DocumentConversionError(f"Converted file not found: {result_path}")

        try:
            return result_path.read_bytes()
        except Exception as exc:
            raise DocumentConversionError(
                f"Failed to read converted file: {exc}"
            ) from exc

    def _analyze_conversion_warnings(
        self,
        request: ConversionRequest,
        converted_data: bytes,
    ) -> tuple[str, ...]:
        """Анализирует возможные предупреждения конвертации."""
        warnings: list[str] = []

        # Проверяем значительное изменение размера файла
        size_ratio = len(converted_data) / len(request.source_data)

        if size_ratio < 0.5:  # Файл уменьшился более чем в 2 раза
            warnings.append(WARN_CONVERSION_QUALITY_LOSS)

        # Предупреждение о потенциально неподдерживаемых функциях
        # (для старых форматов doc/xls)
        if request.from_type in (DocumentType.WORD_DOC, DocumentType.EXCEL_XLS):
            warnings.append(WARN_CONVERSION_FEATURES_UNSUPPORTED)

        return tuple(warnings)

    async def _cleanup_temp_files(
        self,
        temp_input_file: Path | None,
        temp_output_dir: Path | None,
    ) -> None:
        """Очищает временные файлы."""
        try:
            if temp_input_file and temp_input_file.exists():
                # Удаляем всю директорию операции
                operation_dir = temp_input_file.parent
                await self._remove_directory(operation_dir)

        except Exception as exc:
            logger.warning(
                "Failed to cleanup temp files",
                temp_input_file=str(temp_input_file) if temp_input_file else None,
                temp_output_dir=str(temp_output_dir) if temp_output_dir else None,
                error=str(exc),
            )

    async def _remove_directory(self, directory: Path) -> None:
        """Асинхронно удаляет директорию."""
        if not directory.exists():
            return

        # Используем rm -rf для надежного удаления
        process = await asyncio.create_subprocess_exec(
            "rm",
            "-rf",
            str(directory),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0 and stderr:
            logger.warning(
                "Failed to remove directory",
                directory=str(directory),
                stderr=stderr.decode("utf-8", errors="ignore"),
            )

    async def _get_libreoffice_version(self) -> str:
        """Получает версию LibreOffice."""
        try:
            process = await asyncio.create_subprocess_exec(
                "libreoffice",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)

            if process.returncode == 0 and stdout:
                version_line = stdout.decode("utf-8", errors="ignore").strip()
                # Извлекаем версию из строки типа "LibreOffice 7.4.0.1"
                parts = version_line.split()
                if len(parts) >= 2:
                    return parts[1]
                return version_line

            return "unknown"

        except Exception:
            return "unknown"

    async def _get_temp_dir_size(self) -> int:
        """Получает размер временной директории в байтах."""
        try:
            if not self._temp_dir.exists():
                return 0

            process = await asyncio.create_subprocess_exec(
                "du",
                "-sb",
                str(self._temp_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )

            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=5.0)

            if process.returncode == 0 and stdout:
                size_str = stdout.decode("utf-8").strip().split()[0]
                return int(size_str)

            return 0

        except Exception:
            return 0
