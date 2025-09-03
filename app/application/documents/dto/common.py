"""Общие вложенные DTO, переиспользуемые в DTO чанков.

Содержит вспомогательные модели геометрии, шрифтов, ссылок, локальных спанов,
контекста таблиц, пути разделов и происхождения.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import ScriptPosition

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
        page (int | None): Номер страницы, начиная с 1.
        x0 (float | None): Левая координата.
        y0 (float | None): Нижняя координата.
        x1 (float | None): Правая координата.
        y1 (float | None): Верхняя координата.
        rotation (float | None): Поворот в градусах.
        unit (str | None): Единицы измерения координат.
    """

    model_config = ConfigDict(frozen=True)

    page: int | None = Field(default=None, ge=1)
    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None
    rotation: float | None = None
    unit: str | None = None


class FontStyleDTO(BaseModel):
    """Шрифтовые атрибуты.

    Attributes:
        family (str | None): Название гарнитуры шрифта.
        size (float | None): Кегль (размер) шрифта.
        bold (bool | None): Полужирное начертание.
        italic (bool | None): Курсив.
        underline (bool | None): Подчёркивание.
        strike (bool | None): Зачёркивание.
        color_hex (str | None): Цвет в формате #RRGGBB или #RRGGBBAA.
        script (ScriptPosition): Вертикальное позиционирование начертания.
        is_mono (bool | None): Моноширинный шрифт.
    """

    model_config = ConfigDict(frozen=True)

    family: str | None = None
    size: float | None = Field(default=None, ge=0)
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    color_hex: str | None = None
    script: ScriptPosition = ScriptPosition.NORMAL
    is_mono: bool | None = None


class LinkDTO(BaseModel):
    """Гиперссылка/якорь.

    Attributes:
        url (str | None): URL-адрес.
        anchor (str | None): Текст якоря.
        tooltip (str | None): Подсказка при наведении.
        internal_bookmark_id (str | None): Внутренний идентификатор закладки.
    """

    model_config = ConfigDict(frozen=True)

    url: str | None = None
    anchor: str | None = None
    tooltip: str | None = None
    internal_bookmark_id: str | None = None


class RichTextSpanDTO(BaseModel):
    """Локальный спан текста с индивидуальным стилем/ссылкой.

    Attributes:
        text (str): Текст спана (не пустой).
        font (FontStyleDTO | None): Переопределение шрифтовых параметров.
        link (LinkDTO | None): Гиперссылка/якорь.
        language (str | None): Язык текста.
        reading_order (int | None): Порядок чтения в пределах блока/строки.
    """

    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1)
    font: FontStyleDTO | None = None
    link: LinkDTO | None = None
    language: str | None = None
    reading_order: int | None = Field(default=None, ge=0)


class TableCellRefDTO(BaseModel):
    """Ссылка на ячейку таблицы (позиция/объединение).

    Attributes:
        table_index (int | None): Индекс таблицы в документе (с 0).
        row_index (int | None): Индекс строки (с 0).
        col_index (int | None): Индекс столбца (с 0).
        row_span (int | None): Вертикальное объединение (>= 1).
        col_span (int | None): Горизонтальное объединение (>= 1).
    """

    model_config = ConfigDict(frozen=True)

    table_index: int | None = Field(default=None, ge=0)
    row_index: int | None = Field(default=None, ge=0)
    col_index: int | None = Field(default=None, ge=0)
    row_span: int | None = Field(default=None, ge=1)
    col_span: int | None = Field(default=None, ge=1)


class TableContextDTO(BaseModel):
    """Контекст таблицы для строк/ячеек (заголовки, подписи).

    Attributes:
        ref (TableCellRefDTO | None): Ссылка на ячейку.
        header_rows (int | None): Количество заголовочных строк.
        header_cols (int | None): Количество заголовочных столбцов.
        column_headers (dict[int, str]): Заголовки столбцов по индексам.
        row_header (str | None): Заголовок строки.
        caption (str | None): Подпись к таблице.
        title (str | None): Заголовок таблицы.
    """

    model_config = ConfigDict(frozen=True)

    ref: TableCellRefDTO | None = None
    header_rows: int | None = Field(default=None, ge=0)
    header_cols: int | None = Field(default=None, ge=0)
    column_headers: dict[int, str] = Field(default_factory=dict)
    row_header: str | None = None
    caption: str | None = None
    title: str | None = None


class SectionPathDTO(BaseModel):
    """Иерархический путь/нумерация разделов.

    Attributes:
        path (list[str]): Путь разделов (цепочка заголовков).
        numbering (str | None): Нумерация раздела (например, 2.1.3).
        heading_level (int | None): Уровень заголовка (>= 1).
    """

    model_config = ConfigDict(frozen=True)

    path: list[str] = Field(default_factory=list)
    numbering: str | None = None
    heading_level: int | None = Field(default=None, ge=1)


class ProvenanceDTO(BaseModel):
    """Происхождение экстракции (кто/чем/когда).

    Attributes:
        extractor_name (str | None): Имя экстрактора.
        extractor_version (str | None): Версия экстрактора.
        library_versions (dict[str, str]): Версии используемых библиотек.
        extracted_at (datetime | None): Время извлечения данных.
        notes (str | None): Примечания/комментарии.
    """

    model_config = ConfigDict(frozen=True)

    extractor_name: str | None = None
    extractor_version: str | None = None
    library_versions: dict[str, str] = Field(default_factory=dict)
    extracted_at: datetime | None = None
    notes: str | None = None
