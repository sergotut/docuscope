"""Доменные модели результатов экстракции документов.

Тонкие модели, описывающие результат экстракции для разных форматов
(DOCX, PDF-текстовый слой, XLSX). Содержат только необходимые поля
для последующей обработки в домене.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.model.documents import Chunk, DocumentId
from app.domain.shared.codes import WarningCode

__all__ = [
    "DocxExtractionResult",
    "PdfTextExtractionResult",
    "XlsxExtractionResult",
]


@dataclass(frozen=True, slots=True)
class DocxExtractionResult:
    """Результат экстракции содержимого из DOCX.

    Attributes:
        doc_id (DocumentId): Идентификатор документа.
        chunks (tuple[Chunk, ...]): Извлечённые фрагменты текста в порядке следования.
        warnings (tuple[WarningCode, ...]): Предупреждения качества/нормализации.
    """

    doc_id: DocumentId
    chunks: tuple[Chunk, ...]
    warnings: tuple[WarningCode, ...] = ()


@dataclass(frozen=True, slots=True)
class PdfTextExtractionResult:
    """Результат экстракции текстового слоя из PDF.

    Attributes:
        doc_id (DocumentId): Идентификатор документа.
        chunks (tuple[Chunk, ...]): Извлечённые фрагменты текста в порядке следования.
        warnings (tuple[WarningCode, ...]): Предупреждения качества/нормализации.
    """

    doc_id: DocumentId
    chunks: tuple[Chunk, ...]
    warnings: tuple[WarningCode, ...] = ()


@dataclass(frozen=True, slots=True)
class XlsxExtractionResult:
    """Результат экстракции содержимого из XLSX.

    Attributes:
        doc_id (DocumentId): Идентификатор документа.
        chunks (tuple[Chunk, ...]): Извлечённые фрагменты текста (строки/ячейки).
        warnings (tuple[WarningCode, ...]): Предупреждения качества/нормализации.
    """

    doc_id: DocumentId
    chunks: tuple[Chunk, ...]
    warnings: tuple[WarningCode, ...] = ()
