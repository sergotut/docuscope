"""Основные модели элементов экстракции и трассировки."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.model.documents import DocumentId

from .context import ListMarker, SectionPath, TableContext
from .enums import ExtractedKind
from .geometry import BBox
from .spans import InlineSpan

__all__ = [
    "ExtractionProvenance",
    "ExtractedItem",
]


@dataclass(frozen=True, slots=True)
class ExtractionProvenance:
    """Трассировка процесса экстракции для аудита и отладки.

    Содержит метаинформацию о том, как и когда был извлечён элемент.
    Помогает в диагностике проблем качества и воспроизведении результатов.

    Attributes:
        extractor_name (str | None): Название используемого экстрактора.
        extractor_version (str | None): Версия экстрактора или адаптера.
        library_versions (tuple[tuple[str, str], ...]): Кортеж пар (библиотека, версия)
            использованных зависимостей.
        extracted_at (datetime | None): Временная метка выполнения экстракции.
        notes (str | None): Дополнительные заметки или предупреждения о процессе.
    """

    extractor_name: str | None = None
    extractor_version: str | None = None
    library_versions: tuple[tuple[str, str], ...] = ()
    extracted_at: datetime | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class ExtractedItem:
    """Минимально достаточный и расширяемый элемент извлечения.

    Представляет единицу контента, извлечённую из документа, с полным
    набором метаданных для downstream-обработки. Дизайн позволяет
    как простое использование (только текст), так и богатую разметку.

    Attributes:
        doc_id (DocumentId): Идентификатор исходного документа.
        order (int): Порядковый номер элемента в документе (с 0).
        kind (ExtractedKind): Тип семантического элемента.
        text (str): Нормализованный текстовый контент элемента.
        spans (tuple[InlineSpan, ...]): Детальная inline-разметка текста.
        language (str | None): Код языка элемента в формате BCP-47.
        section (SectionPath | None): Иерархический путь в структуре документа.
        list_marker (ListMarker | None): Информация о маркере списка (для LIST_ITEM).
        table_ctx (TableContext | None): Контекст таблицы (заголовки, позиция ячейки).
        page_number (int | None): Номер страницы в документе (с 1).
        bbox (BBox | None): Геометрическая позиция на странице.
        confidence (float | None): Оценка уверенности экстракции от 0.0 до 1.0.
        provenance (ExtractionProvenance | None): Трассировочная информация о процессе
            извлечения.
    """

    doc_id: DocumentId
    order: int
    kind: ExtractedKind
    text: str

    spans: tuple[InlineSpan, ...] = ()
    language: str | None = None
    section: SectionPath | None = None
    list_marker: ListMarker | None = None
    table_ctx: TableContext | None = None

    page_number: int | None = None
    bbox: BBox | None = None

    confidence: float | None = None
    provenance: ExtractionProvenance | None = None
