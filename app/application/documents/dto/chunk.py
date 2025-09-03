"""DTO фрагментов для извлечённого контента (DOCX/XLSX/PDF-текст).

Назначение: транспорт между адаптерами, нормализацией, сплиттером и эмбеддером,
а также хранение богатых метаданных для фильтрации, цитирования и трассировки.
"""

from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from app.domain.model.documents import ChunkId, DocumentId
from app.domain.model.documents.types import DocumentFamily, DocumentType
from app.domain.shared.codes import WarningCode

from .common import (
    ProvenanceDTO,
    RichTextSpanDTO,
    SectionPathDTO,
    TableContextDTO,
)
from .enums import ChunkKind, ListStyle
from .positions import DocxPositionDTO, PdfPositionDTO, XlsxCellDTO
from .table import TableDTO

__all__ = [
    "BaseChunkDTO",
    "DocxChunkDTO",
    "PdfTextChunkDTO",
    "XlsxChunkDTO",
    "AnyChunkDTO",
]


class BaseChunkDTO(BaseModel):
    """Базовый DTO фрагмента (chunk) для всех форматов.

    Поле text — то, что пойдёт в эмбеддер. Остальные поля — метаданные для
    ретривала, фильтрации, цитирования и диагностики.

    Attributes:
        chunk_id (ChunkId): Идентификатор фрагмента.
        doc_id (DocumentId): Идентификатор документа.
        order (int): Порядковый номер фрагмента (>= 0).
        kind (ChunkKind): Тип текстового элемента.
        text (str): Текст фрагмента (не пустой).
        spans (list[RichTextSpanDTO]): Локальные спаны текста с разметкой.
        language (str | None): Язык фрагмента.
        section (SectionPathDTO | None): Иерархическая позиция в документе.
        list_level (int | None): Уровень вложенности списка.
        list_style (ListStyle): Стиль списка.
        table_ctx (TableContextDTO | None): Контекст таблицы для строк/ячеек.
        origin_family (DocumentFamily | str | None): Семейство исходного документа.
        origin_type (DocumentType | str | None): Строгий тип исходного документа.
        original_filename (str | None): Оригинальное имя файла (если доступно).
        storage_object (str | None): Имя файла в объектном хранилище.
        checksum_sha256 (str | None): Хеш контента для идемпотентности/аудита.
        page_number (int | None): Номер страницы (если применимо).
        warnings (list[WarningCode]): Коды предупреждений.
        confidence (float | None): Уверенность экстрактора [0..1].
        provenance (ProvenanceDTO | None): Происхождение (кто/чем/когда).
        table_json (TableDTO | None): Каноническая таблица.
        table_markdown (str | None): Markdown-представление таблицы.
        table_markdown_checksum (str | None): Контрольная сумма Markdown.
        ext (dict[str, Any] | None): Расширение на будущее (без ослабления схемы).
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        validate_assignment=False,
    )

    # Идентичность и порядок
    chunk_id: ChunkId = Field(min_length=1)
    doc_id: DocumentId = Field(min_length=1)
    order: int = Field(ge=0)

    # Содержимое и локальная разметка
    kind: ChunkKind
    text: str = Field(min_length=1)
    spans: list[RichTextSpanDTO] = Field(default_factory=list)
    language: str | None = None

    # Структура документа
    section: SectionPathDTO | None = None
    list_level: int | None = Field(default=None, ge=0)
    list_style: ListStyle = ListStyle.NONE
    table_ctx: TableContextDTO | None = None

    # Происхождение/файловые мета
    origin_family: DocumentFamily | str | None = None
    origin_type: DocumentType | str | None = None
    original_filename: str | None = None
    storage_object: str | None = None
    checksum_sha256: str | None = None

    # Геометрия/страница (если применимо)
    page_number: int | None = Field(default=None, ge=1)

    # Качество/диагностика
    warnings: list[WarningCode] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    provenance: ProvenanceDTO | None = None

    # Двойственное представление для таблиц
    table_json: TableDTO | None = None
    table_markdown: str | None = None
    table_markdown_checksum: str | None = None

    # Расширение на будущее (без ослабления схемы)
    ext: dict[str, Any] | None = None


class DocxChunkDTO(BaseChunkDTO):
    """Чанк, извлечённый из DOCX.

    Attributes:
        source_format (Literal["docx"]): Буквально "docx".
        docx (DocxPositionDTO | None): Позиционные метаданные DOCX.
    """

    model_config = ConfigDict(frozen=True)

    source_format: Literal["docx"] = "docx"
    docx: DocxPositionDTO | None = None


class PdfTextChunkDTO(BaseChunkDTO):
    """Чанк, извлечённый из PDF (текстовый слой).

    Attributes:
        source_format (Literal["pdf_text"]): Буквально "pdf_text".
        pdf (PdfPositionDTO | None): Позиционные метаданные PDF.
    """

    model_config = ConfigDict(frozen=True)

    source_format: Literal["pdf_text"] = "pdf_text"
    pdf: PdfPositionDTO


class XlsxChunkDTO(BaseChunkDTO):
    """Чанк, извлечённый из XLSX (обычно строка или значимая ячейка).

    Attributes:
        source_format (Literal["xlsx"]): Буквально "xlsx".
        xlsx (XlsxCellDTO | None): Позиционные/семантические метаданные XLSX.
    """

    model_config = ConfigDict(frozen=True)

    source_format: Literal["xlsx"] = "xlsx"
    xlsx: XlsxCellDTO


AnyChunkDTO = Union[DocxChunkDTO, PdfTextChunkDTO, XlsxChunkDTO]
