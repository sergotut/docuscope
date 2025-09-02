"""Перечисления, используемые DTO чанков."""

from __future__ import annotations

from enum import Enum

__all__ = [
    "ChunkKind",
    "ListStyle",
    "ScriptPosition",
    "ColumnType",
]


class ChunkKind(str, Enum):
    """Тип текстового элемента в исходном документе.

    Attributes:
        PARAGRAPH: Абзац обычного текста.
        HEADING: Заголовок раздела.
        LIST_ITEM: Элемент списка (пункт).
        TABLE_ROW: Строка таблицы.
        TABLE_CELL: Ячейка таблицы.
        CAPTION: Подпись к таблице/рисунку.
        FOOTNOTE: Сноска.
        ENDNOTE: Концевая сноска.
        HEADER: Верхний колонтитул.
        FOOTER: Нижний колонтитул.
        TEXT_BOX: Встроенная текстовая область.
        QUOTE: Цитата.
        CODE: Фрагмент кода.
        OTHER: Другое.
    """

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    CAPTION = "caption"
    FOOTNOTE = "footnote"
    ENDNOTE = "endnote"
    HEADER = "header"
    FOOTER = "footer"
    TEXT_BOX = "text_box"
    QUOTE = "quote"
    CODE = "code"
    OTHER = "other"


class ListStyle(str, Enum):
    """Стиль списка.

    Attributes:
        NONE: Без списочного оформления.
        BULLET: Маркированный список.
        DECIMAL: Нумерованный (десятичный) список.
        ROMAN_LOWER: Римские цифры в нижнем регистре.
        ROMAN_UPPER: Римские цифры в верхнем регистре.
        ALPHA_LOWER: Буквенная нумерация в нижнем регистре.
        ALPHA_UPPER: Буквенная нумерация в верхнем регистре.
        OTHER: Иной стиль.
    """

    NONE = "none"
    BULLET = "bullet"
    DECIMAL = "decimal"
    ROMAN_LOWER = "roman_lower"
    ROMAN_UPPER = "roman_upper"
    ALPHA_LOWER = "alpha_lower"
    ALPHA_UPPER = "alpha_upper"
    OTHER = "other"


class ScriptPosition(str, Enum):
    """Вертикальное позиционирование начертания.

    Attributes:
        NORMAL: Обычная базовая линия.
        SUPERSCRIPT: Верхний индекс.
        SUBSCRIPT: Нижний индекс.
    """

    NORMAL = "normal"
    SUPERSCRIPT = "superscript"
    SUBSCRIPT = "subscript"


class ColumnType(str, Enum):
    """Тип данных столбца таблицы (для канонического JSON).

    Attributes:
        TEXT: Текст.
        NUMBER: Число с плавающей точкой.
        INTEGER: Целое число.
        DATE: Дата (ISO-8601).
        DATETIME: Дата/время (ISO-8601).
        CURRENCY: Денежное значение.
        BOOLEAN: Логический тип.
        PERCENT: Процент.
        DOMAIN: Доменно-специфический тип (например, ИНН/IBAN и т.п.).
    """

    TEXT = "text"
    NUMBER = "number"
    INTEGER = "integer"
    DATE = "date"
    DATETIME = "datetime"
    CURRENCY = "currency"
    BOOLEAN = "boolean"
    PERCENT = "percent"
    DOMAIN = "domain"
