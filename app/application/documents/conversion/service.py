"""Сервис конвертации документов (application-слой).

Тонкая обёртка над доменным портом `DocumentConverterPort`.
Не дублирует доменную логику и модели, отвечает за координацию и логирование.
"""

from __future__ import annotations

import structlog

from app.domain.model.documents import (
    ConversionRequest,
    ConversionResult,
    DocumentType,
)
from app.domain.ports import DocumentConverterPort

__all__ = ["DocumentConversionService"]


logger = structlog.get_logger(__name__)


class DocumentConversionService:
    """Высокоуровневый сервис конвертации документов.

    Делегирует фактическую конвертацию в реализацию `DocumentConverterPort`.
    Сервис предназначен для использования в workflow верхнего уровня.

    Attributes:
        _converter: Реализация порта конвертации документов.
    """

    def __init__(self, converter: DocumentConverterPort) -> None:
        """Инициализирует сервис конвертации.

        Args:
            converter: Порт конвертера документов.
        """
        self._converter = converter
        self._logger = logger.bind(service="document_conversion")

    async def convert(self, request: ConversionRequest) -> ConversionResult:
        """Выполняет конвертацию документа согласно запросу.

        Args:
            request: Запрос на конвертацию.

        Returns:
            ConversionResult: Результат конвертации.
        """
        self._logger.info(
            "Begin document conversion",
            document_id=request.document_id,
            from_type=request.from_type,
            to_type=request.to_type,
        )

        result = await self._converter.convert(request)

        if result.is_successful:
            self._logger.info(
                "Document converted",
                document_id=result.document_id,
                target_type=result.target_type,
                size_bytes=result.size_bytes,
                warnings=bool(result.warnings),
            )
        else:
            self._logger.warning(
                "Document conversion failed",
                document_id=result.document_id,
                target_type=result.target_type,
                error=result.error_message,
            )

        return result

    def is_supported(self, from_type: DocumentType, to_type: DocumentType) -> bool:
        """Проверяет поддержку конвертации между типами (делегат порта).

        Args:
            from_type: Исходный тип документа.
            to_type: Целевой тип документа.

        Returns:
            bool: True, если конвертация поддерживается портом.
        """
        return self._converter.is_conversion_supported(from_type, to_type)

    @property
    def supported_conversions(self) -> frozenset[tuple[DocumentType, DocumentType]]:
        """Возвращает множество поддерживаемых пар конвертации (делегат порта)."""
        return self._converter.supported_conversions
