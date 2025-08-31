"""Пакет libreoffice_client: низкоуровневые компоненты LibreOffice.

Содержит модели, протоколы и утилиты для работы с LibreOffice процессами.
"""

from .models import (
    DOMAIN_TO_LIBREOFFICE_FORMAT,
    ConversionCommand,
    ConversionMetrics,
    LibreOfficeFormat,
    ProcessInfo,
    ProcessState,
)
from .process_manager import LibreOfficeProcessManager
from .protocols import LibreOfficeProcessProtocol
from .utils import get_libreoffice_version, validate_libreoffice_installation

__all__ = [
    # Модели
    "ProcessState",
    "ConversionCommand",
    "ProcessInfo",
    "ConversionMetrics",
    "LibreOfficeFormat",
    "DOMAIN_TO_LIBREOFFICE_FORMAT",
    # Менеджер процессов
    "LibreOfficeProcessManager",
    # Протоколы
    "LibreOfficeProcessProtocol",
    # Утилиты
    "get_libreoffice_version",
    "validate_libreoffice_installation",
]
