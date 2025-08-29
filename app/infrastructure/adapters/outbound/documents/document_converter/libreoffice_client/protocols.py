"""Протоколы для LibreOffice процессов и компонентов.

Определяет абстракции для низкоуровневых компонентов LibreOffice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import ConversionCommand, ProcessInfo

__all__ = ["LibreOfficeProcessProtocol"]


class LibreOfficeProcessProtocol(Protocol):
    """Протокол для взаимодействия с LibreOffice процессом.

    Определяет минимальный интерфейс для управления LibreOffice процессом,
    позволяя создавать различные реализации (subprocess, docker, remote).
    """

    @property
    def process_info(self) -> ProcessInfo:
        """Информация о процессе.

        Returns:
            ProcessInfo: Текущее состояние и метрики процесса.
        """
        ...

    async def start(self) -> None:
        """Запускает LibreOffice процесс.

        Raises:
            DocumentConversionError: При ошибке запуска процесса.
        """
        ...

    async def stop(self) -> None:
        """Останавливает LibreOffice процесс.

        Выполняет graceful shutdown с возможностью принудительного завершения.
        """
        ...

    async def convert(self, command: ConversionCommand) -> Path:
        """Выполняет конвертацию документа.

        Args:
            command (ConversionCommand): Команда конвертации с параметрами.

        Returns:
            Path: Путь к сконвертированному файлу.

        Raises:
            DocumentConversionError: При ошибке конвертации.
        """
        ...

    async def is_alive(self) -> bool:
        """Проверяет, жив ли процесс.

        Returns:
            bool: True, если процесс активен и отвечает.
        """
        ...

    async def health_check(self) -> bool:
        """Выполняет проверку здоровья процесса.

        Более детальная проверка, чем is_alive(), может включать
        тестовую конвертацию небольшого документа.

        Returns:
            bool: True, если процесс готов к работе.
        """
        ...
