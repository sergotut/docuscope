"""Формат-специфичные позиционные DTO."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import BBoxDTO, FontStyleDTO, TableCellRefDTO
from .enums import ListStyle

__all__ = [
    "DocxPositionDTO",
    "PdfPositionDTO",
    "XlsxCellDTO",
]


class DocxPositionDTO(BaseModel):
    """Позиционная и стилевая информация для DOCX-чанков.

    Attributes:
        section_index (Optional[int]): Индекс секции документа.
        paragraph_index (Optional[int]): Индекс абзаца.
        run_index (Optional[int]): Индекс спана/рани.
        style_name (Optional[str]): Имя применённого стиля.
        heading_level (Optional[int]): Уровень заголовка (если применимо).
        list_level (Optional[int]): Уровень вложенности списка.
        list_style (ListStyle): Стиль списка.
        list_num_id (Optional[int]): Идентификатор нумерации.
        in_header (bool): Признак нахождения во внешнем колонтитуле.
        in_footer (bool): Признак нахождения в нижнем колонтитуле.
        footnote_id (Optional[int]): Идентификатор сноски.
        endnote_id (Optional[int]): Идентификатор концевой сноски.
        table (Optional[TableCellRefDTO]): Позиция в таблице, если элемент расположен
            внутри таблицы.
    """

    model_config = ConfigDict(frozen=True)

    section_index: Optional[int] = Field(default=None, ge=0)
    paragraph_index: Optional[int] = Field(default=None, ge=0)
    run_index: Optional[int] = Field(default=None, ge=0)
    style_name: Optional[str] = None
    heading_level: Optional[int] = Field(default=None, ge=1)
    list_level: Optional[int] = Field(default=None, ge=0)
    list_style: ListStyle = ListStyle.NONE
    list_num_id: Optional[int] = Field(default=None, ge=0)
    in_header: bool = False
    in_footer: bool = False
    footnote_id: Optional[int] = Field(default=None, ge=0)
    endnote_id: Optional[int] = Field(default=None, ge=0)
    table: Optional[TableCellRefDTO] = None


class PdfPositionDTO(BaseModel):
    """Позиционная информация для PDF (текстовый слой).

    Attributes:
        page_number (int): Номер страницы (>= 1).
        block_index (Optional[int]): Индекс блока.
        line_index (Optional[int]): Индекс строки.
        span_index (Optional[int]): Индекс спана/фрагмента.
        column_index (Optional[int]): Индекс колонки.
        reading_order (Optional[int]): Порядок чтения.
        bbox (Optional[BBoxDTO]): Геометрия блока.
        font (Optional[FontStyleDTO]): Шрифтовые атрибуты.
        is_hyphenated_join (Optional[bool]): Признак склейки переноса.
    """

    model_config = ConfigDict(frozen=True)

    page_number: int = Field(ge=1)
    block_index: Optional[int] = Field(default=None, ge=0)
    line_index: Optional[int] = Field(default=None, ge=0)
    span_index: Optional[int] = Field(default=None, ge=0)
    column_index: Optional[int] = Field(default=None, ge=0)
    reading_order: Optional[int] = Field(default=None, ge=0)
    bbox: Optional[BBoxDTO] = None
    font: Optional[FontStyleDTO] = None
    is_hyphenated_join: Optional[bool] = None


class XlsxCellDTO(BaseModel):
    """Позиционная/семантическая информация для XLSX-ячейки.

    Attributes:
        sheet_name (str): Имя листа.
        sheet_index (int): Индекс листа (с 0).
        row_index (int): Индекс строки (с 0).
        col_index (int): Индекс столбца (с 0).
        a1_address (Optional[str]): Адрес в нотации A1.
        is_merged (Optional[bool]): Признак объединённой ячейки.
        merged_range (Optional[str]): Диапазон объединения.
        formula (Optional[str]): Формула (если есть).
        value (Optional[str]): Нормализованное значение.
        display_value (Optional[str]): Отображаемое значение.
        number_format (Optional[str]): Числовой формат.
        data_type (Optional[str]): Тип данных (string/number/date/bool/formula...).
        hyperlink (Optional[str]): Гиперссылка.
        comment (Optional[str]): Комментарий.
        row_header (Optional[str]): Заголовок строки.
        col_header (Optional[str]): Заголовок столбца.
        table (Optional[TableCellRefDTO]): Позиция в таблице.
    """

    model_config = ConfigDict(frozen=True)

    sheet_name: str
    sheet_index: int = Field(ge=0)
    row_index: int = Field(ge=0)
    col_index: int = Field(ge=0)
    a1_address: Optional[str] = None
    is_merged: Optional[bool] = None
    merged_range: Optional[str] = None
    formula: Optional[str] = None
    value: Optional[str] = None
    display_value: Optional[str] = None
    number_format: Optional[str] = None
    data_type: Optional[str] = None
    hyperlink: Optional[str] = None
    comment: Optional[str] = None
    row_header: Optional[str] = None
    col_header: Optional[str] = None
    table: Optional[TableCellRefDTO] = None
