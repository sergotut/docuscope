"""DI адаптер для LibreOffice конвертера документов.

Создаёт и настраивает экземпляр LibreOfficeDocumentConverter
с параметрами из конфигурации приложения.
"""

from __future__ import annotations

import structlog

from app.domain.ports import DocumentConverterPort
from app.infrastructure.adapters.outbound.documents.document_converter import (
    LibreOfficeConfig,
    LibreOfficeDocumentConverter,
)
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)

__all__ = [
    "LibreOfficeDocumentConverterAdapter",
]


class LibreOfficeDocumentConverterAdapter:
    """DI адаптер для создания LibreOffice конвертера документов.

    Создаёт singleton экземпляр LibreOfficeDocumentConverter с настройками
    из конфигурации приложения. Обеспечивает управление пулом процессов
    и оптимальное использование ресурсов.
    """

    _instance: DocumentConverterPort | None = None

    @classmethod
    async def create(cls) -> DocumentConverterPort:
        """Создаёт или возвращает singleton экземпляр конвертера.

        Returns:
            DocumentConverterPort: Настроенный экземпляр LibreOffice конвертера.
        """
        if cls._instance is None:
            cls._instance = await cls._create_instance()

        return cls._instance

    @classmethod
    async def _create_instance(cls) -> DocumentConverterPort:
        """Создаёт новый экземпляр LibreOffice конвертера с настройками.

        Returns:
            DocumentConverterPort: Новый экземпляр конвертера.
        """
        common_config = settings.documents.common
        conversion_config = settings.documents.conversion

        # Преобразуем настройки в LibreOfficeConfig
        temp_dir = common_config.temp_base_path

        # Вычисляем таймауты на основе общих настроек и множителей
        process_idle_timeout = int(
            common_config.default_timeout_seconds
            * conversion_config.process_idle_timeout_multiplier
        )
        conversion_timeout = int(
            common_config.default_timeout_seconds
            * conversion_config.conversion_timeout_multiplier
        )

        libreoffice_config = LibreOfficeConfig(
            min_processes=conversion_config.min_processes,
            max_processes=conversion_config.max_processes,
            process_idle_timeout=process_idle_timeout,
            conversion_timeout=conversion_timeout,
            temp_dir=temp_dir,
            cleanup_interval=common_config.cleanup_interval_seconds,
            max_file_size_mb=common_config.max_document_size_mb,
        )

        converter = LibreOfficeDocumentConverter(config=libreoffice_config)

        # Инициализируем конвертер (запускаем пул процессов)
        await converter._ensure_initialized()

        logger.info(
            "LibreOfficeDocumentConverter created",
            min_processes=conversion_config.min_processes,
            max_processes=conversion_config.max_processes,
            process_idle_timeout=process_idle_timeout,
            conversion_timeout=conversion_timeout,
            max_file_size_mb=common_config.max_document_size_mb,
            temp_dir=str(temp_dir) if temp_dir else None,
            enable_process_recycling=conversion_config.enable_process_recycling,
            max_operations_per_process=conversion_config.max_operations_per_process,
        )

        return converter

    @classmethod
    async def cleanup(cls) -> None:
        """Очищает ресурсы конвертера.

        Должен вызываться при завершении работы приложения
        для корректного закрытия пула процессов.
        """
        if cls._instance is not None:
            if hasattr(cls._instance, "_cleanup"):
                await cls._instance._cleanup()  # type: ignore[attr-defined]
            cls._instance = None
            logger.info("LibreOfficeDocumentConverter cleaned up")
