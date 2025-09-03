"""Формат-специфичные позиционные DTO."""

from __future__ import annotations

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
        section_index (int | None): Индекс секции документа.
        paragraph_index (int | None): Индекс абзаца.
        run_index (int | None): Индекс спана/рани.
        style_name (str | None): Имя применённого стиля.
        heading_level (int | None): Уровень заголовка (если применимо).
        list_level (int | None): Уровень вложенности списка.
        list_style (ListStyle): Стиль списка.
        list_num_id (int | None): Идентификатор нумерации.
        in_header (bool): Признак нахождения во внешнем колонтитуле.
        in_footer (bool): Признак нахождения в нижнем колонтитуле.
        footnote_id (int | None): Идентификатор сноски.
        endnote_id (int | None): Идентификатор концевой сноски.
        table (TableCellRefDTO | None): Позиция в таблице, если элемент расположен
            внутри таблицы.
    """

    model_config = ConfigDict(frozen=True)

    section_index: int | None = Field(default=None, ge=0)
    paragraph_index: int | None = Field(default=None, ge=0)
    run_index: int | None = Field(default=None, ge=0)
    style_name: str | None = None
    heading_level: int | None = Field(default=None, ge=1)
    list_level: int | None = Field(default=None, ge=0)
    list_style: ListStyle = ListStyle.NONE
    list_num_id: int | None = Field(default=None, ge=0)
    in_header: bool = False
    in_footer: bool = False
    footnote_id: int | None = Field(default=None, ge=0)
    endnote_id: int | None = Field(default=None, ge=0)
    table: TableCellRefDTO | None = None


class PdfPositionDTO(BaseModel):
    """Позиционная информация для PDF (текстовый слой).

    Attributes:
        page_number (int): Номер страницы (>= 1).
        block_index (int | None): Индекс блока.
        line_index (int | None): Индекс строки.
        span_index (int | None): Индекс спана/фрагмента.
        column_index (int | None): Индекс колонки.
        reading_order (int | None): Порядок чтения.
        bbox (BBoxDTO | None): Геометрия блока.
        font (FontStyleDTO | None): Шрифтовые атрибуты.
        is_hyphenated_join (bool | None): Признак склейки переноса.
    """

    model_config = ConfigDict(frozen=True)

    page_number: int = Field(ge=1)
    block_index: int | None = Field(default=None, ge=0)
    line_index: int | None = Field(default=None, ge=0)
    span_index: int | None = Field(default=None, ge=0)
    column_index: int | None = Field(default=None, ge=0)
    reading_order: int | None = Field(default=None, ge=0)
    bbox: BBoxDTO | None = None
    font: FontStyleDTO | None = None
    is_hyphenated_join: bool | None = None


class XlsxCellDTO(BaseModel):
    """Позиционная/семантическая информация для XLSX-ячейки.

    Attributes:
        sheet_name (str): Имя листа.
        sheet_index (int): Индекс листа (с 0).
        row_index (int): Индекс строки (с 0).
        col_index (int): Индекс столбца (с 0).
        a1_address (str | None): Адрес в нотации A1.
        is_merged (bool | None): Признак объединённой ячейки.
        merged_range (str | None): Диапазон объединения.
        formula (str | None): Формула (если есть).
        value (str | None): Нормализованное значение.
        display_value (str | None): Отображаемое значение.
        number_format (str | None): Числовой формат.
        data_type (str | None): Тип данных (string/number/date/bool/formula...).
        hyperlink (str | None): Гиперссылка.
        comment (str | None): Комментарий.
        row_header (str | None): Заголовок строки.
        col_header (str | None): Заголовок столбца.
        table (TableCellRefDTO | None): Позиция в таблице.
    """

    model_config = ConfigDict(frozen=True)

    sheet_name: str
    sheet_index: int = Field(ge=0)
    row_index: int = Field(ge=0)
    col_index: int = Field(ge=0)
    a1_address: str | None = None
    is_merged: bool | None = None
    merged_range: str | None = None
    formula: str | None = None
    value: str | None = None
    display_value: str | None = None
    number_format: str | None = None
    data_type: str | None = None
    hyperlink: str | None = None
    comment: str | None = None
    row_header: str | None = None
    col_header: str | None = None
    table: TableCellRefDTO | None = None
