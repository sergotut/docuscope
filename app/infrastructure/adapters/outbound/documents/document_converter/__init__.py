"""Адаптеры конвертации документов.

Содержит реализации DocumentConverterPort для различных движков:
- LibreOffice: высокопроизводительный адаптер с process pooling

Каждый адаптер реализует протокол DocumentConverterPort, изолируя
инфраструктурную логику от бизнес-слоя.
"""

from .libreoffice import (
    LibreOfficeConfig,
    LibreOfficeDocumentConverter,
    create_development_converter,
    create_production_converter,
)

__all__ = [
    # Основной адаптер
    "LibreOfficeDocumentConverter",
    # Конфигурация
    "LibreOfficeConfig",
    "create_production_converter",
    "create_development_converter",
]
