"""DI адаптер для валидации входных документов.

Создаёт и настраивает экземпляр DocumentInputValidationService
с параметрами из конфигурации приложения.
"""

from __future__ import annotations

import structlog

from app.application.documents.policies.input_validation import (
    DocumentInputConstraints,
    DocumentInputValidationService,
)
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)

__all__ = [
    "DocumentInputValidationAdapter",
]


class DocumentInputValidationAdapter:
    """DI адаптер для создания сервиса валидации входных документов.

    Создаёт singleton экземпляр DocumentInputValidationService с настройками
    из конфигурации приложения. Обеспечивает единообразную валидацию
    входящих документов согласно прикладной политике.
    """

    _instance: DocumentInputValidationService | None = None

    @classmethod
    def create(cls) -> DocumentInputValidationService:
        """Создаёт или возвращает singleton экземпляр валидатора.

        Returns:
            DocumentInputValidationService: Настроенный экземпляр валидатора.
        """
        if cls._instance is None:
            cls._instance = cls._create_instance()

        return cls._instance

    @classmethod
    def _create_instance(cls) -> DocumentInputValidationService:
        """Создаёт новый экземпляр валидатора с настройками.

        Returns:
            DocumentInputValidationService: Новый экземпляр валидатора.
        """
        common_config = settings.documents.common

        constraints = DocumentInputConstraints(
            max_document_size_mb=common_config.max_document_size_mb,
            max_filename_length=common_config.max_filename_length,
        )

        validator = DocumentInputValidationService(constraints)

        logger.info(
            "DocumentInputValidationService created",
            max_document_size_mb=common_config.max_document_size_mb,
            max_filename_length=common_config.max_filename_length,
        )

        return validator
