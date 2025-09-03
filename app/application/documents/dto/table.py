"""Канонические DTO таблиц (JSON-представление), используемые в DTO чанков.

Служат источником истины для табличных данных, а также для генерации
альтернативных представлений (например, Markdown-снимка).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .enums import ColumnType

__all__ = [
    "TableDTO",
    "TableColumnDTO",
    "TableRowDTO",
    "TableCellDTO",
]


class TableColumnDTO(BaseModel):
    """Описание столбца таблицы.

    Attributes:
        index (int): Индекс столбца (с 0).
        name (str): Имя столбца.
        type (ColumnType): Тип данных столбца.
        unit (str | None): Единица измерения.
        format (str | None): Формат отображения.
        description (str | None): Описание столбца.
    """

    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    name: str
    type: ColumnType = ColumnType.TEXT
    unit: str | None = None
    format: str | None = None
    description: str | None = None


class TableCellDTO(BaseModel):
    """Каноническая ячейка таблицы с нормализованными значениями.

    Attributes:
        row_index (int): Индекс строки (с 0).
        col_index (int): Индекс столбца (с 0).
        value_norm (str | None): Нормализованное значение.
        value_display (str | None): Отображаемое значение.
        number_value (float | None): Числовое значение.
        date_value (str | None): Дата (ISO-8601).
        bool_value (bool | None): Логическое значение.
        formula (str | None): Формула.
        hyperlink (str | None): Гиперссылка.
        comment (str | None): Комментарий.
        merged (bool | None): Признак объединения ячеек.
        merged_range (str | None): Диапазон объединения.
    """

    model_config = ConfigDict(frozen=True)

    row_index: int = Field(ge=0)
    col_index: int = Field(ge=0)
    value_norm: str | None = None
    value_display: str | None = None
    number_value: float | None = None
    date_value: str | None = None
    bool_value: bool | None = None
    formula: str | None = None
    hyperlink: str | None = None
    comment: str | None = None
    merged: bool | None = None
    merged_range: str | None = None


class TableRowDTO(BaseModel):
    """Строка таблицы.

    Attributes:
        index (int): Индекс строки (с 0).
        cells (list[TableCellDTO]): Список ячеек строки.
        is_header (bool): Флаг заголовочной строки.
    """

    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    cells: list[TableCellDTO] = Field(default_factory=list)
    is_header: bool = False


class TableDTO(BaseModel):
    """Каноническая таблица (источник истины для табличных данных).

    Attributes:
        name (str | None): Имя таблицы.
        caption (str | None): Подпись к таблице.
        header_rows (int): Количество заголовочных строк (>= 0).
        columns (list[TableColumnDTO]): Описание столбцов.
        rows (list[TableRowDTO]): Список строк.
        n_rows (int): Количество строк (>= 0).
        n_cols (int): Количество столбцов (>= 0).
        source_kind (Literal["xlsx", "pdf_text", "docx"]): Источник таблицы.
        sheet_name (str | None): Имя листа (для XLSX).
        page_number (int | None): Номер страницы (для PDF).
    """

    model_config = ConfigDict(frozen=True)

    name: str | None = None
    caption: str | None = None
    header_rows: int = Field(default=1, ge=0)
    columns: list[TableColumnDTO] = Field(default_factory=list)
    rows: list[TableRowDTO] = Field(default_factory=list)
    n_rows: int = Field(ge=0)
    n_cols: int = Field(ge=0)
    source_kind: Literal["xlsx", "pdf_text", "docx"]
    sheet_name: str | None = None
    page_number: int | None = Field(default=None, ge=1)
