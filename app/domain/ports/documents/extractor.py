"""Порт экстрактора содержимого документов.

Абстракция над движками извлечения текста и таблиц из исходных файлов
разных форматов (DOCX, PDF-текстовый слой, XLSX). Предоставляет операции
экстракции и методы health-check по аналогии с другими портами.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import DocumentExtractorHealthReport
from app.domain.model.documents.extraction import (
    DocxExtractionResult,
    PdfTextExtractionResult,
    XlsxExtractionResult,
)

__all__ = ["DocumentExtractorPort"]


@runtime_checkable
class DocumentExtractorPort(Protocol):
    """Абстрактный асинхронный порт экстрактора документов."""

    async def extract_docx(self, *, object_key: str) -> DocxExtractionResult:
        """Извлекает содержимое из DOCX.

        Args:
            object_key (str): Ключ объекта исходного файла в хранилище.

        Returns:
            DocxExtractionResult: Извлечённые чанки и предупреждения.
        """
        ...

    async def extract_pdf_text(self, *, object_key: str) -> PdfTextExtractionResult:
        """Извлекает текстовый слой из PDF-файла.

        Args:
            object_key (str): Ключ объекта исходного файла в хранилище.

        Returns:
            PdfTextExtractionResult: Извлечённые чанки и предупреждения.
        """
        ...

    async def extract_xlsx(self, *, object_key: str) -> XlsxExtractionResult:
        """Извлекает содержимое из XLSX (значимые строки/ячейки/таблицы).

        Args:
            object_key (str): Ключ объекта исходного файла в хранилище.

        Returns:
            XlsxExtractionResult: Извлечённые чанки и предупреждения.
        """
        ...

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если экстрактор доступен и готов к работе.
        """
        ...

    async def health(self) -> DocumentExtractorHealthReport:
        """Подробный health-репорт экстрактора.

        Returns:
            DocumentExtractorHealthReport: Метаинформация о состоянии экстрактора.
        """
        ...


