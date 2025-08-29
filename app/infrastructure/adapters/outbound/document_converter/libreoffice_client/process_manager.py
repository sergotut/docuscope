"""Менеджер LibreOffice процессов для высокопроизводительной конвертации.

Реализует pool паттерн для управления множественными LibreOffice процессами,
обеспечивая масштабируемость для тысяч пользователей.
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path
from typing import Any

import structlog

from app.domain.exceptions import DocumentConversionError

from .models import (
    LIBREOFFICE_IDLE_TIMEOUT,
    LIBREOFFICE_MAX_FAILURES,
    ConversionCommand,
    ConversionMetrics,
    ProcessInfo,
    ProcessState,
)

__all__ = ["LibreOfficeProcessManager"]

logger = structlog.get_logger(__name__)


class LibreOfficeProcessManager:
    """Высокопроизводительный менеджер LibreOffice процессов.

    Особенности:
    - Process pool для параллельной обработки
    - Автоматическое масштабирование под нагрузку
    - Мониторинг здоровья процессов и перезапуск при сбоях
    - Graceful shutdown с завершением активных задач
    - Метрики производительности в реальном времени

    Attributes:
        min_processes (int): Минимальное количество процессов в пуле.
        max_processes (int): Максимальное количество процессов.
        process_idle_timeout (int): Таймаут простоя процесса в секундах.
    """

    def __init__(
        self,
        *,
        min_processes: int = 2,
        max_processes: int = 10,
        process_idle_timeout: int = LIBREOFFICE_IDLE_TIMEOUT,
        temp_dir: Path | None = None,
    ) -> None:
        """Инициализирует менеджер процессов.

        Args:
            min_processes (int): Минимальное количество процессов.
            max_processes (int): Максимальное количество процессов.
            process_idle_timeout (int): Таймаут простоя в секундах.
            temp_dir (Path | None): Директория для временных файлов.
        """
        self._min_processes = min_processes
        self._max_processes = max_processes
        self._process_idle_timeout = process_idle_timeout
        self._temp_dir = (
            temp_dir or Path(tempfile.gettempdir()) / "docuscope_libreoffice"
        )

        # Состояние менеджера
        self._processes: dict[int, ProcessInfo] = {}
        self._available_processes: asyncio.Queue[int] = asyncio.Queue()
        self._conversion_queue: asyncio.Queue[
            tuple[ConversionCommand, asyncio.Future[Path]]
        ] = asyncio.Queue()
        self._metrics = ConversionMetrics()
        self._shutdown_event = asyncio.Event()
        self._cleanup_task: asyncio.Task[Any] | None = None
        self._worker_tasks: list[asyncio.Task[Any]] = []

        # Блокировки для thread safety
        self._processes_lock = asyncio.Lock()
        self._metrics_lock = asyncio.Lock()

        logger.info(
            "LibreOffice process manager initialized",
            min_processes=min_processes,
            max_processes=max_processes,
            temp_dir=str(self._temp_dir),
        )

    async def start(self) -> None:
        """Запускает менеджер процессов."""
        if self._cleanup_task is not None:
            raise RuntimeError("Process manager is already started")

        # Создаем временную директорию
        self._temp_dir.mkdir(parents=True, exist_ok=True)

        # Запускаем минимальное количество процессов
        for _ in range(self._min_processes):
            await self._start_process()

        # Запускаем фоновые задачи
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        # Запускаем воркеры для обработки очереди
        for i in range(self._max_processes):
            worker_task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self._worker_tasks.append(worker_task)

        logger.info(
            "LibreOffice process manager started",
            active_processes=len(self._processes)
        )

    async def stop(self) -> None:
        """Останавливает менеджер процессов с graceful shutdown."""
        if self._cleanup_task is None:
            return

        logger.info("Stopping LibreOffice process manager...")
        self._shutdown_event.set()

        # Останавливаем фоновые задачи
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Останавливаем воркеров
        for task in self._worker_tasks:
            task.cancel()

        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        # Останавливаем все процессы
        async with self._processes_lock:
            for process_info in self._processes.values():
                await self._stop_process(process_info)
            self._processes.clear()

        self._cleanup_task = None
        self._worker_tasks.clear()
        logger.info("LibreOffice process manager stopped")

    async def convert(self, command: ConversionCommand) -> Path:
        """Выполняет конвертацию документа.
        
        Args:
            command (ConversionCommand): Команда конвертации.
            
        Returns:
            Path: Путь к сконвертированному файлу.
            
        Raises:
            DocumentConversionError: При ошибках конвертации.
        """
        if self._shutdown_event.is_set():
            raise DocumentConversionError("Process manager is shutting down")

        start_time = time.time()
        future: asyncio.Future[Path] = asyncio.Future()

        # Добавляем задачу в очередь
        await self._conversion_queue.put((command, future))

        async with self._metrics_lock:
            self._metrics.queue_size = self._conversion_queue.qsize()

        try:
            # Ожидаем результат с таймаутом
            result = await asyncio.wait_for(future, timeout=command.timeout_seconds)

            # Обновляем метрики
            conversion_time_ms = (time.time() - start_time) * 1000
            async with self._metrics_lock:
                self._metrics.successful_conversions += 1
                self._metrics.total_time_ms += conversion_time_ms

            return result

        except asyncio.TimeoutError as exc:
            async with self._metrics_lock:
                self._metrics.failed_conversions += 1
            raise DocumentConversionError(
                f"Conversion timeout after {command.timeout_seconds}s"
            ) from exc

        except Exception as e:
            async with self._metrics_lock:
                self._metrics.failed_conversions += 1

            if isinstance(e, DocumentConversionError):
                raise

            raise DocumentConversionError(f"Conversion failed: {e}") from e

    async def get_metrics(self) -> ConversionMetrics:
        """Возвращает текущие метрики производительности."""
        async with self._metrics_lock:
            # Создаем копию метрик с актуальными данными
            metrics = ConversionMetrics(
                total_conversions=self._metrics.total_conversions,
                successful_conversions=self._metrics.successful_conversions,
                failed_conversions=self._metrics.failed_conversions,
                total_time_ms=self._metrics.total_time_ms,
                queue_wait_time_ms=self._metrics.queue_wait_time_ms,
                active_processes=len(self._processes),
                queue_size=self._conversion_queue.qsize(),
            )

        return metrics

    async def _worker_loop(self, worker_name: str) -> None:
        """Основной цикл воркера для обработки задач конвертации."""
        logger.debug("Worker started", worker=worker_name)

        try:
            while not self._shutdown_event.is_set():
                try:
                    # Получаем задачу из очереди с таймаутом
                    command, future = await asyncio.wait_for(
                        self._conversion_queue.get(), timeout=1.0
                    )

                    if future.cancelled():
                        continue

                    # Выполняем конвертацию
                    try:
                        result = await self._execute_conversion(command)
                        if not future.cancelled():
                            future.set_result(result)
                    except Exception as e:
                        if not future.cancelled():
                            future.set_exception(e)

                except asyncio.TimeoutError:
                    continue  # Проверяем shutdown_event

        except asyncio.CancelledError:
            pass

        logger.debug("Worker stopped", worker=worker_name)

    async def _execute_conversion(self, command: ConversionCommand) -> Path:
        """Выполняет конвертацию с использованием доступного процесса."""
        queue_start_time = time.time()

        # Получаем доступный процесс
        process_id = await self._get_available_process()

        queue_wait_time_ms = (time.time() - queue_start_time) * 1000
        async with self._metrics_lock:
            self._metrics.queue_wait_time_ms += queue_wait_time_ms
            self._metrics.total_conversions += 1

        try:
            # Выполняем конвертацию
            result_path = await self._run_conversion(process_id, command)

            # Отмечаем успешное использование процесса
            async with self._processes_lock:
                if process_id in self._processes:
                    self._processes[process_id].mark_used()

            return result_path

        except Exception:
            # Отмечаем неудачу
            async with self._processes_lock:
                if process_id in self._processes:
                    process_info = self._processes[process_id]
                    process_info.mark_failed()

                    # Перезапускаем процесс при превышении лимита неудач
                    if process_info.failures_count >= LIBREOFFICE_MAX_FAILURES:
                        logger.warning(
                            "Process exceeded failure limit, restarting",
                            pid=process_id,
                            failures=process_info.failures_count,
                        )
                        await self._restart_process(process_id)

            raise

        finally:
            # Возвращаем процесс в пул
            await self._available_processes.put(process_id)

    async def _get_available_process(self) -> int:
        """Получает доступный процесс из пула."""
        # Пытаемся получить процесс без ожидания
        try:
            return self._available_processes.get_nowait()
        except asyncio.QueueEmpty:
            pass

        # Если нет доступных процессов, пытаемся создать новый
        async with self._processes_lock:
            if len(self._processes) < self._max_processes:
                process_id = await self._start_process()
                return process_id

        # Ждем освобождения процесса
        return await self._available_processes.get()

    async def _start_process(self) -> int:
        """Запускает новый LibreOffice процесс."""
        # Создаем уникальную директорию для процесса
        process_dir = self._temp_dir / f"process_{int(time.time() * 1000000)}"
        process_dir.mkdir(parents=True, exist_ok=True)

        # Команда запуска LibreOffice в headless режиме
        cmd = [
            "libreoffice",
            "--headless",
            "--norestore",
            "--invisible",
            "--nodefault",
            "--nolockcheck",
            "--nologo",
            "--nofirststartwizard",
            "--accept=socket,host=127.0.0.1,port=0;urp;StarOffice.ServiceManager",
        ]

        try:
            # Запускаем процесс
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
                cwd=process_dir,
            )

            if process.pid is None:
                raise DocumentConversionError("Failed to start LibreOffice process")

            # Ждем запуска процесса
            await asyncio.sleep(2)  # Даем время на инициализацию

            # Проверяем, что процесс еще жив
            if process.returncode is not None:
                stderr_output = ""
                if process.stderr:
                    stderr_data = await process.stderr.read()
                    stderr_output = stderr_data.decode('utf-8', errors='ignore')

                raise DocumentConversionError(
                    f"LibreOffice process died during startup: {stderr_output}"
                )

            # Создаем информацию о процессе
            process_info = ProcessInfo(pid=process.pid, state=ProcessState.READY)
            self._processes[process.pid] = process_info

            # Добавляем процесс в пул доступных
            await self._available_processes.put(process.pid)

            logger.debug("LibreOffice process started", pid=process.pid)
            return process.pid

        except Exception as exc:
            logger.error("Failed to start LibreOffice process", error=str(exc))
            raise DocumentConversionError(
                f"Failed to start LibreOffice process: {exc}"
            ) from exc

    async def _stop_process(self, process_info: ProcessInfo) -> None:
        """Останавливает LibreOffice процесс."""
        if process_info.pid is None:
            return

        try:
            # Пытаемся мягко завершить процесс
            process = await asyncio.create_subprocess_exec(
                "kill", "-TERM", str(process_info.pid),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(process.wait(), timeout=5.0)

        except (asyncio.TimeoutError, ProcessLookupError):
            # Принудительно завершаем процесс
            try:
                process = await asyncio.create_subprocess_exec(
                    "kill", "-KILL", str(process_info.pid),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await process.wait()
            except ProcessLookupError:
                pass  # Процесс уже завершен

        process_info.state = ProcessState.STOPPING
        logger.debug("LibreOffice process stopped", pid=process_info.pid)

    async def _restart_process(self, process_id: int) -> None:
        """Перезапускает процесс."""
        async with self._processes_lock:
            if process_id in self._processes:
                process_info = self._processes[process_id]
                await self._stop_process(process_info)
                del self._processes[process_id]

                # Запускаем новый процесс
                await self._start_process()

    async def _run_conversion(
        self,
        process_id: int,
        command: ConversionCommand
    ) -> Path:
        """Выполняет конвертацию с использованием конкретного процесса."""
        # Формируем команду конвертации
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to",
            command.target_format.value,
            "--outdir",
            str(command.output_dir),
            str(command.input_path),
        ]

        try:
            # Выполняем конвертацию
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=command.timeout_seconds,
            )

            if process.returncode != 0:
                stderr_text = (
                    stderr.decode('utf-8', errors='ignore')
                    if stderr
                    else "Unknown error"
                )
                raise DocumentConversionError(
                    f"LibreOffice conversion failed: {stderr_text}"
                )

            # Находим результирующий файл
            expected_name = command.input_path.stem + f".{command.target_format.value}"
            result_path = command.output_dir / expected_name

            if not result_path.exists():
                raise DocumentConversionError(
                    f"Conversion result not found: {result_path}"
                )

            return result_path

        except asyncio.TimeoutError as exc:
            raise DocumentConversionError(
                f"Conversion timeout after {command.timeout_seconds}s"
            ) from exc

        except Exception as exc:
            if isinstance(exc, DocumentConversionError):
                raise
            raise DocumentConversionError(
                f"Conversion execution failed: {exc}"
            ) from exc

    async def _cleanup_loop(self) -> None:
        """Фоновая задача для очистки неиспользуемых процессов."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Проверяем каждую минуту

                current_time = time.time()
                processes_to_remove = []

                async with self._processes_lock:
                    for process_id, process_info in self._processes.items():
                        # Удаляем процессы, которые простаивают слишком долго
                        if (
                            len(self._processes) > self._min_processes
                            and process_info.idle_seconds > self._process_idle_timeout
                            and process_info.state == ProcessState.READY
                        ) or process_info.state == ProcessState.FAILED:
                            processes_to_remove.append(process_id)

                # Удаляем процессы
                for process_id in processes_to_remove:
                    async with self._processes_lock:
                        if process_id in self._processes:
                            process_info = self._processes[process_id]
                            await self._stop_process(process_info)
                            del self._processes[process_id]

                            logger.debug(
                                "Cleaned up idle process",
                                pid=process_id,
                                idle_seconds=process_info.idle_seconds,
                            )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup loop", error=str(e))
