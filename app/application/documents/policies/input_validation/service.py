"""Сервис для валидации входа для документов.

Сервис валидирует размеры и имя файла до выполнения детекции/конвертации/сохранения.
"""

from __future__ import annotations

import structlog

from app.domain.exceptions import DomainValidationError, FileSizeTooLargeError
from app.domain.model.shared import Blob

from .models import DocumentInputConstraints

__all__ = [
    "DocumentInputValidationService",
]


class DocumentInputValidationService:
    """Сервис fail-fast проверки блоба документа.

    Проверяет базовые ограничения входа до запуска остального workflow.
    """

    def __init__(self, constraints: DocumentInputConstraints) -> None:
        """Инициализирует сервис с заданными ограничениями.

        Args:
            constraints (DocumentInputConstraints): Ограничения политики.
        """
        self._c = constraints
        self._logger = structlog.get_logger(__name__).bind(
            service="document_input_validation"
        )

    def validate_blob(self, blob: Blob) -> None:
        """Проверяет размер и имя файла согласно ограничениям.

        Args:
            blob (Blob): Входной блоб с данными и метаданными.

        Raises:
            FileSizeTooLargeError: Если размер превышает лимит по МБ.
            DomainValidationError: Если имя файла слишком длинное.
        """
        # Размер файла
        size_mb = blob.size / (1024 * 1024)
        if size_mb > self._c.max_document_size_mb:
            self._logger.warning(
                "file_too_large",
                size_mb=round(size_mb, 2),
                limit_mb=self._c.max_document_size_mb,
            )
            raise FileSizeTooLargeError(
                f"File size {size_mb:.1f} MB exceeds limit "
                f"{self._c.max_document_size_mb} MB"
            )

        # Длина имени файла, если оно задано
        if blob.filename and len(blob.filename) > self._c.max_filename_length:
            self._logger.warning(
                "filename_too_long",
                length=len(blob.filename),
                limit=self._c.max_filename_length,
            )
            raise DomainValidationError(
                f"Filename length {len(blob.filename)} exceeds limit "
                f"{self._c.max_filename_length}"
            )
