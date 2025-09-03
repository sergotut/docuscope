"""Перечисления для экстракции документов."""

from __future__ import annotations

from enum import Enum

__all__ = [
    "ExtractedKind",
    "ListStyle",
    "ScriptPosition",
]


class ExtractedKind(Enum):
    """Тип семантического элемента исходного документа.

    Определяет категорию контента, извлечённого из документа, что позволяет
    downstream-системам применять соответствующую обработку и форматирование.

    Attributes:
        PARAGRAPH: Обычный абзац текста.
        HEADING: Заголовок раздела или подраздела.
        LIST_ITEM: Элемент списка (маркированного или нумерованного).
        TABLE_ROW: Строка таблицы как единое целое.
        TABLE_CELL: Отдельная ячейка таблицы.
        CAPTION: Подпись к таблице, рисунку или другому элементу.
        FOOTNOTE: Нижняя сноска.
        ENDNOTE: Концевая сноска.
        HEADER: Верхний колонтитул.
        FOOTER: Нижний колонтитул.
        TEXT_BOX: Текстовый блок или врезка.
        QUOTE: Цитата или выделенный блок.
        CODE: Блок кода или формулы.
        OTHER: Прочий тип контента.
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


class ListStyle(Enum):
    """Стиль нумерации/маркировки списка.

    Определяет тип маркера или нумерации, используемый в списке.
    Помогает сохранить семантику оригинального форматирования.

    Attributes:
        NONE: Без маркера (обычный текст).
        BULLET: Маркированный список (точки, дефисы).
        DECIMAL: Арабская нумерация (1, 2, 3).
        ROMAN_LOWER: Римская нумерация строчными (i, ii, iii).
        ROMAN_UPPER: Римская нумерация прописными (I, II, III).
        ALPHA_LOWER: Буквенная нумерация строчными (a, b, c).
        ALPHA_UPPER: Буквенная нумерация прописными (A, B, C).
        OTHER: Нестандартный стиль маркировки.
    """

    NONE = "none"
    BULLET = "bullet"
    DECIMAL = "decimal"
    ROMAN_LOWER = "roman_lower"
    ROMAN_UPPER = "roman_upper"
    ALPHA_LOWER = "alpha_lower"
    ALPHA_UPPER = "alpha_upper"
    OTHER = "other"


class ScriptPosition(Enum):
    """Вертикальное позиционирование начертания шрифта.

    Определяет расположение текста относительно базовой линии.
    Используется для корректного отображения индексов, степеней и т.п.

    Attributes:
        NORMAL: Обычное расположение на базовой линии.
        SUPERSCRIPT: Надстрочный индекс (степень, сноска).
        SUBSCRIPT: Подстрочный индекс (химические формулы, математика).
    """

    NORMAL = "normal"
    SUPERSCRIPT = "superscript"
    SUBSCRIPT = "subscript"
