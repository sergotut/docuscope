"""Канонические DTO таблиц (JSON-представление), используемые в DTO чанков.

Служат источником истины для табличных данных, а также для генерации
альтернативных представлений (например, Markdown-снимка).
"""

from __future__ import annotations

from typing import Optional, Literal

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
        unit (Optional[str]): Единица измерения.
        format (Optional[str]): Формат отображения.
        description (Optional[str]): Описание столбца.
    """

    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    name: str
    type: ColumnType = ColumnType.TEXT
    unit: Optional[str] = None
    format: Optional[str] = None
    description: Optional[str] = None


class TableCellDTO(BaseModel):
    """Каноническая ячейка таблицы с нормализованными значениями.

    Attributes:
        row_index (int): Индекс строки (с 0).
        col_index (int): Индекс столбца (с 0).
        value_norm (Optional[str]): Нормализованное значение.
        value_display (Optional[str]): Отображаемое значение.
        number_value (Optional[float]): Числовое значение.
        date_value (Optional[str]): Дата (ISO-8601).
        bool_value (Optional[bool]): Логическое значение.
        formula (Optional[str]): Формула.
        hyperlink (Optional[str]): Гиперссылка.
        comment (Optional[str]): Комментарий.
        merged (Optional[bool]): Признак объединения ячеек.
        merged_range (Optional[str]): Диапазон объединения.
    """

    model_config = ConfigDict(frozen=True)

    row_index: int = Field(ge=0)
    col_index: int = Field(ge=0)
    value_norm: Optional[str] = None
    value_display: Optional[str] = None
    number_value: Optional[float] = None
    date_value: Optional[str] = None
    bool_value: Optional[bool] = None
    formula: Optional[str] = None
    hyperlink: Optional[str] = None
    comment: Optional[str] = None
    merged: Optional[bool] = None
    merged_range: Optional[str] = None


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
        name (Optional[str]): Имя таблицы.
        caption (Optional[str]): Подпись к таблице.
        header_rows (int): Количество заголовочных строк (>= 0).
        columns (list[TableColumnDTO]): Описание столбцов.
        rows (list[TableRowDTO]): Список строк.
        n_rows (int): Количество строк (>= 0).
        n_cols (int): Количество столбцов (>= 0).
        source_kind (Literal["xlsx", "pdf_text", "docx"]): Источник таблицы.
        sheet_name (Optional[str]): Имя листа (для XLSX).
        page_number (Optional[int]): Номер страницы (для PDF).
    """

    model_config = ConfigDict(frozen=True)

    name: Optional[str] = None
    caption: Optional[str] = None
    header_rows: int = Field(default=1, ge=0)
    columns: list[TableColumnDTO] = Field(default_factory=list)
    rows: list[TableRowDTO] = Field(default_factory=list)
    n_rows: int = Field(ge=0)
    n_cols: int = Field(ge=0)
    source_kind: Literal["xlsx", "pdf_text", "docx"]
    sheet_name: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
