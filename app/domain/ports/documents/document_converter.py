"""Порт конвертации документов между форматами.

Предоставляет абстракцию для преобразования документов старых форматов
в современные (doc->docx, xls->xlsx) с контролем качества и предупреждениями.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import DocumentConverterHealthReport
from app.domain.model.documents.conversion import ConversionRequest, ConversionResult
from app.domain.model.documents.types import DocumentType

__all__ = ["DocumentConverterPort"]


@runtime_checkable
class DocumentConverterPort(Protocol):
    """Абстрактный асинхронный порт конвертации документов между форматами.

    Предоставляет интерфейс для преобразования документов из устаревших
    форматов в современные с сохранением содержимого и метаданных.

    Все операции конвертации асинхронные из-за I/O-интенсивной природы
    преобразования файлов и возможного использования внешних инструментов.
    """

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
        ...

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
        ...

    @property
    def supported_conversions(self) -> frozenset[tuple[DocumentType, DocumentType]]:
        """Возвращает множество поддерживаемых пар конвертации.

        Returns:
            frozenset[tuple[DocumentType, DocumentType]]: Неизменяемое множество
            кортежей (исходный_тип, целевой_тип) для всех поддерживаемых
            конвертаций.
        """
        ...

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если сервис конвертации доступен и готов к работе.
        """
        ...

    async def health(self) -> DocumentConverterHealthReport:
        """Подробный health-репорт.

        Returns:
            DocumentConverterHealthReport: Метаинформация о состоянии конвертера,
            включая статистику конвертаций, производительность и доступность
            внешних инструментов.
        """
        ...

    @property
    def max_concurrent_conversions(self) -> int:
        """Максимальное количество параллельных конвертаций.

        Returns:
            int: Лимит одновременно выполняемых операций конвертации.
        """
        ...
