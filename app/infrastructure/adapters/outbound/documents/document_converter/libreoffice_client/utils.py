"""Утилиты для работы с LibreOffice.

Содержит вспомогательные функции для проверки установки LibreOffice,
получения версии, валидации параметров и других операций.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import structlog

__all__ = [
    "get_libreoffice_version",
    "validate_libreoffice_installation",
    "get_libreoffice_executable",
    "cleanup_temp_directory",
]

logger = structlog.get_logger(__name__)


async def get_libreoffice_version() -> str:
    """Получает версию установленного LibreOffice.

    Returns:
        str: Версия LibreOffice или "unknown" при ошибке.
    """
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

    except Exception as exc:
        logger.warning("Failed to get LibreOffice version", error=str(exc))
        return "unknown"


async def validate_libreoffice_installation() -> tuple[bool, str]:
    """Проверяет корректность установки LibreOffice.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
            is_valid: True, если LibreOffice установлен и работает.
            error_message: Описание ошибки при is_valid=False.
    """
    try:
        # Проверяем наличие исполняемого файла
        executable = get_libreoffice_executable()
        if not executable:
            return False, "LibreOffice executable not found in PATH"

        # Проверяем запуск с --version
        process = await asyncio.create_subprocess_exec(
            str(executable),
            "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)

        if process.returncode != 0:
            stderr_text = (
                stderr.decode("utf-8", errors="ignore") if stderr else "Unknown error"
            )
            return False, f"LibreOffice version check failed: {stderr_text}"

        # Проверяем headless режим
        process = await asyncio.create_subprocess_exec(
            str(executable),
            "--headless",
            "--help",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)

        if process.returncode != 0:
            return False, "LibreOffice headless mode not supported"

        return True, ""

    except asyncio.TimeoutError:
        return False, "LibreOffice validation timeout"

    except Exception as exc:
        return False, f"LibreOffice validation error: {exc}"


def get_libreoffice_executable() -> Path | None:
    """Находит исполняемый файл LibreOffice.

    Returns:
        Path | None: Путь к LibreOffice или None, если не найден.
    """
    # Проверяем стандартные имена исполняемых файлов
    executable_names = [
        "libreoffice",
        "libreoffice7.4",
        "libreoffice7.3",
        "libreoffice7.2",
        "libreoffice7.1",
        "libreoffice7.0",
        "soffice",
    ]

    for name in executable_names:
        executable_path = shutil.which(name)
        if executable_path:
            return Path(executable_path)

    # Проверяем стандартные пути установки
    standard_paths = [
        "/usr/bin/libreoffice",
        "/usr/local/bin/libreoffice",
        "/opt/libreoffice/program/soffice",
        "/snap/bin/libreoffice",
    ]

    for path_str in standard_paths:
        path = Path(path_str)
        if path.exists() and path.is_file():
            return path

    return None


async def cleanup_temp_directory(directory: Path, *, max_age_hours: int = 24) -> int:
    """Очищает временную директорию от старых файлов.

    Args:
        directory (Path): Директория для очистки.
        max_age_hours (int): Максимальный возраст файлов в часах.

    Returns:
        int: Количество удаленных файлов.
    """
    if not directory.exists():
        return 0

    removed_count = 0
    max_age_seconds = max_age_hours * 3600
    current_time = asyncio.get_event_loop().time()

    try:
        for item in directory.iterdir():
            try:
                # Получаем время модификации
                mtime = item.stat().st_mtime
                age_seconds = current_time - mtime

                if age_seconds > max_age_seconds:
                    if item.is_file():
                        item.unlink()
                        removed_count += 1
                    elif item.is_dir():
                        # Рекурсивно удаляем директорию
                        await _remove_directory_async(item)
                        removed_count += 1

            except Exception as exc:
                logger.warning(
                    "Failed to remove temp item",
                    item=str(item),
                    error=str(exc),
                )

        logger.debug(
            "Temp directory cleanup completed",
            directory=str(directory),
            removed_count=removed_count,
            max_age_hours=max_age_hours,
        )

        return removed_count

    except Exception as exc:
        logger.error(
            "Failed to cleanup temp directory",
            directory=str(directory),
            error=str(exc),
        )
        return 0


async def _remove_directory_async(directory: Path) -> None:
    """Асинхронно удаляет директорию с содержимым."""
    try:
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
                "Failed to remove directory with rm -rf",
                directory=str(directory),
                stderr=stderr.decode("utf-8", errors="ignore"),
            )

    except Exception as exc:
        logger.warning(
            "Failed to remove directory",
            directory=str(directory),
            error=str(exc),
        )
