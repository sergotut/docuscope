"""Модели для inline-разметки и стилизации текста."""

from __future__ import annotations

from dataclasses import dataclass

from .enums import ScriptPosition

__all__ = [
    "FontStyle",
    "Link",
    "InlineSpan",
]


@dataclass(frozen=True, slots=True)
class FontStyle:
    """Шрифтовые атрибуты для локальных спанов текста.

    Описывает форматирование отдельного фрагмента текста внутри элемента.
    Позволяет сохранить богатую типографику оригинального документа.

    Attributes:
        family (str | None): Название семейства шрифтов.
        size (float | None): Размер шрифта в пунктах или пикселях.
        bold (bool | None): Признак жирного начертания.
        italic (bool | None): Признак курсивного начертания.
        underline (bool | None): Признак подчёркивания.
        strike (bool | None): Признак зачёркивания.
        color_hex (str | None): Цвет текста в шестнадцатеричном формате.
        script (ScriptPosition): Вертикальное позиционирование.
        is_mono (bool | None): Признак моноширинного шрифта.
    """

    family: str | None = None
    size: float | None = None
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    color_hex: str | None = None
    script: ScriptPosition = ScriptPosition.NORMAL
    is_mono: bool | None = None


@dataclass(frozen=True, slots=True)
class Link:
    """Гиперссылка или внутренний якорь.

    Представляет связанную с текстом ссылку на внешний ресурс
    или внутренний элемент документа.

    Attributes:
        url (str | None): URL внешней ссылки.
        anchor (str | None): Якорь внутри текущего документа.
        tooltip (str | None): Всплывающая подсказка при наведении.
        internal_bookmark_id (str | None): Внутренний идентификатор закладки
            в документе.
    """

    url: str | None = None
    anchor: str | None = None
    tooltip: str | None = None
    internal_bookmark_id: str | None = None


@dataclass(frozen=True, slots=True)
class InlineSpan:
    """Локальный спан текста с собственным стилем и/или ссылкой.

    Представляет фрагмент текста внутри элемента с индивидуальным
    форматированием. Позволяет сохранить детальную разметку документа.

    Attributes:
        text (str): Текст спана (не может быть пустым).
        font (FontStyle | None): Шрифтовые атрибуты спана.
        link (Link | None): Связанная гиперссылка, если есть.
        language (str | None): Код языка спана в формате BCP-47 (например, "ru-RU").
        reading_order (int | None): Порядок чтения внутри родительского блока.
    """

    text: str
    font: FontStyle | None = None
    link: Link | None = None
    language: str | None = None
    reading_order: int | None = None
