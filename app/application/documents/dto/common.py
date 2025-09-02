"""Общие вложенные DTO, переиспользуемые в DTO чанков.

Содержит вспомогательные модели геометрии, шрифтов, ссылок, локальных спанов,
контекста таблиц, пути разделов и происхождения.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import ListStyle, ScriptPosition

__all__ = [
    "BBoxDTO",
    "FontStyleDTO",
    "LinkDTO",
    "RichTextSpanDTO",
    "TableCellRefDTO",
    "TableContextDTO",
    "SectionPathDTO",
    "ProvenanceDTO",
]


class BBoxDTO(BaseModel):
    """Геометрия текстового блока/спана.

    Координаты задаются в единицах источника (например, pt/px). Для PDF
    критично для восстановления порядка чтения и корректного цитирования.

    Attributes:
        page (Optional[int]): Номер страницы, начиная с 1.
        x0 (Optional[float]): Левая координата.
        y0 (Optional[float]): Нижняя координата.
        x1 (Optional[float]): Правая координата.
        y1 (Optional[float]): Верхняя координата.
        rotation (Optional[float]): Поворот в градусах.
        unit (Optional[str]): Единицы измерения координат.
    """

    model_config = ConfigDict(frozen=True)

    page: Optional[int] = Field(default=None, ge=1)
    x0: Optional[float] = None
    y0: Optional[float] = None
    x1: Optional[float] = None
    y1: Optional[float] = None
    rotation: Optional[float] = None
    unit: Optional[str] = None


class FontStyleDTO(BaseModel):
    """Шрифтовые атрибуты.

    Attributes:
        family (Optional[str]): Название гарнитуры шрифта.
        size (Optional[float]): Кегль (размер) шрифта.
        bold (Optional[bool]): Полужирное начертание.
        italic (Optional[bool]): Курсив.
        underline (Optional[bool]): Подчёркивание.
        strike (Optional[bool]): Зачёркивание.
        color_hex (Optional[str]): Цвет в формате #RRGGBB или #RRGGBBAA.
        script (ScriptPosition): Вертикальное позиционирование начертания.
        is_mono (Optional[bool]): Моноширинный шрифт.
    """

    model_config = ConfigDict(frozen=True)

    family: Optional[str] = None
    size: Optional[float] = Field(default=None, ge=0)
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strike: Optional[bool] = None
    color_hex: Optional[str] = None
    script: ScriptPosition = ScriptPosition.NORMAL
    is_mono: Optional[bool] = None


class LinkDTO(BaseModel):
    """Гиперссылка/якорь.

    Attributes:
        url (Optional[str]): URL-адрес.
        anchor (Optional[str]): Текст якоря.
        tooltip (Optional[str]): Подсказка при наведении.
        internal_bookmark_id (Optional[str]): Внутренний идентификатор закладки.
    """

    model_config = ConfigDict(frozen=True)

    url: Optional[str] = None
    anchor: Optional[str] = None
    tooltip: Optional[str] = None
    internal_bookmark_id: Optional[str] = None


class RichTextSpanDTO(BaseModel):
    """Локальный спан текста с индивидуальным стилем/ссылкой.

    Attributes:
        text (str): Текст спана (не пустой).
        font (Optional[FontStyleDTO]): Переопределение шрифтовых параметров.
        link (Optional[LinkDTO]): Гиперссылка/якорь.
        language (Optional[str]): Язык текста.
        reading_order (Optional[int]): Порядок чтения в пределах блока/строки.
    """

    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1)
    font: Optional[FontStyleDTO] = None
    link: Optional[LinkDTO] = None
    language: Optional[str] = None
    reading_order: Optional[int] = Field(default=None, ge=0)


class TableCellRefDTO(BaseModel):
    """Ссылка на ячейку таблицы (позиция/объединение).

    Attributes:
        table_index (Optional[int]): Индекс таблицы в документе (с 0).
        row_index (Optional[int]): Индекс строки (с 0).
        col_index (Optional[int]): Индекс столбца (с 0).
        row_span (Optional[int]): Вертикальное объединение (>= 1).
        col_span (Optional[int]): Горизонтальное объединение (>= 1).
    """

    model_config = ConfigDict(frozen=True)

    table_index: Optional[int] = Field(default=None, ge=0)
    row_index: Optional[int] = Field(default=None, ge=0)
    col_index: Optional[int] = Field(default=None, ge=0)
    row_span: Optional[int] = Field(default=None, ge=1)
    col_span: Optional[int] = Field(default=None, ge=1)


class TableContextDTO(BaseModel):
    """Контекст таблицы для строк/ячеек (заголовки, подписи).

    Attributes:
        ref (Optional[TableCellRefDTO]): Ссылка на ячейку.
        header_rows (Optional[int]): Количество заголовочных строк.
        header_cols (Optional[int]): Количество заголовочных столбцов.
        column_headers (dict[int, str]): Заголовки столбцов по индексам.
        row_header (Optional[str]): Заголовок строки.
        caption (Optional[str]): Подпись к таблице.
        title (Optional[str]): Заголовок таблицы.
    """

    model_config = ConfigDict(frozen=True)

    ref: Optional[TableCellRefDTO] = None
    header_rows: Optional[int] = Field(default=None, ge=0)
    header_cols: Optional[int] = Field(default=None, ge=0)
    column_headers: dict[int, str] = Field(default_factory=dict)
    row_header: Optional[str] = None
    caption: Optional[str] = None
    title: Optional[str] = None


class SectionPathDTO(BaseModel):
    """Иерархический путь/нумерация разделов.

    Attributes:
        path (list[str]): Путь разделов (цепочка заголовков).
        numbering (Optional[str]): Нумерация раздела (например, 2.1.3).
        heading_level (Optional[int]): Уровень заголовка (>= 1).
    """

    model_config = ConfigDict(frozen=True)

    path: list[str] = Field(default_factory=list)
    numbering: Optional[str] = None
    heading_level: Optional[int] = Field(default=None, ge=1)


class ProvenanceDTO(BaseModel):
    """Происхождение экстракции (кто/чем/когда).

    Attributes:
        extractor_name (Optional[str]): Имя экстрактора.
        extractor_version (Optional[str]): Версия экстрактора.
        library_versions (dict[str, str]): Версии используемых библиотек.
        extracted_at (Optional[datetime]): Время извлечения данных.
        notes (Optional[str]): Примечания/комментарии.
    """

    model_config = ConfigDict(frozen=True)

    extractor_name: Optional[str] = None
    extractor_version: Optional[str] = None
    library_versions: dict[str, str] = Field(default_factory=dict)
    extracted_at: Optional[datetime] = None
    notes: Optional[str] = None
