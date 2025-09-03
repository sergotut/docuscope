"""Модели контекста для структурных элементов документа."""

from __future__ import annotations

from dataclasses import dataclass

from .enums import ListStyle

__all__ = [
    "SectionPath",
    "ListMarker",
    "TableCellRef",
    "TableContext",
]


@dataclass(frozen=True, slots=True)
class SectionPath:
    """Иерархический путь по разделам документа.

    Представляет структурную позицию элемента в иерархии заголовков
    и разделов документа. Помогает восстановить оглавление и навигацию.

    Attributes:
        path (tuple[str, ...]): Кортеж заголовков от корня документа до текущего
            раздела. Например: ("Общие положения", "Права и обязанности сторон",
            "Ответственность сторон").
        numbering (str | None): Нумерация раздела в формате "X.Y.Z" (например, "2.1.3").
        heading_level (int | None): Уровень заголовка (1 для H1, 2 для H2 и т.д.).
    """

    path: tuple[str, ...] = ()
    numbering: str | None = None
    heading_level: int | None = None


@dataclass(frozen=True, slots=True)
class ListMarker:
    """Маркер списка для элементов LIST_ITEM.

    Содержит информацию о форматировании и позиции элемента в списке.
    Позволяет корректно восстановить структуру вложенных списков.

    Attributes:
        level (int): Уровень вложенности списка, начиная с 0 для корневого уровня.
        style (ListStyle): Стиль нумерации или маркировки списка.
        num_id (int | None): Внутренний идентификатор абзаца списка (для DOCX),
            если известен.
        text (str | None): Видимый текст маркера (например, "1.", "•", "a)").
    """

    level: int = 0
    style: ListStyle = ListStyle.NONE
    num_id: int | None = None
    text: str | None = None


@dataclass(frozen=True, slots=True)
class TableCellRef:
    """Ссылка на ячейку таблицы и её объединение (span).

    Определяет точную позицию ячейки в таблице и её размеры
    при объединении смежных ячеек.

    Attributes:
        table_index (int | None): Порядковый номер таблицы на странице/в секции (с 0).
        row_index (int | None): Индекс строки в таблице (с 0).
        col_index (int | None): Индекс колонки в таблице (с 0).
        row_span (int): Количество объединённых строк (>=1).
        col_span (int): Количество объединённых колонок (>=1).
    """

    table_index: int | None = None
    row_index: int | None = None
    col_index: int | None = None
    row_span: int = 1
    col_span: int = 1


@dataclass(frozen=True, slots=True)
class TableContext:
    """Контекст таблицы для строки или ячейки.

    Предоставляет семантическую информацию о структуре таблицы,
    включая заголовки и метаданные, необходимые для понимания
    содержимого ячейки в контексте всей таблицы.

    Attributes:
        header_rows (int): Количество строк заголовка таблицы (thead).
        header_cols (int): Количество колонок заголовка (левые stub-колонки).
        column_headers (tuple[str, ...]): Заголовки колонок слева направо.
        row_header (str | None): Заголовок строки (содержимое первой ячейки строки).
        caption (str | None): Подпись к таблице (обычно сверху или снизу).
        title (str | None): Название/заголовок таблицы.
        cell_ref (TableCellRef | None): Привязка к конкретной ячейке
            (если элемент — ячейка).
    """

    header_rows: int = 0
    header_cols: int = 0
    column_headers: tuple[str, ...] = ()
    row_header: str | None = None
    caption: str | None = None
    title: str | None = None
    cell_ref: TableCellRef | None = None
