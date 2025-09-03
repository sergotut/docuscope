"""Пакет экстракции: модели и опции для извлечения контента из документов.

Содержит все необходимые типы и конфигурации для процесса экстракции
структурированного контента из различных форматов документов.
"""

from __future__ import annotations

from .context import ListMarker, SectionPath, TableCellRef, TableContext
from .enums import ExtractedKind, ListStyle, ScriptPosition
from .geometry import BBox
from .items import ExtractedItem, ExtractionProvenance
from .options import ExtractionOptions, ExtractorCapability
from .spans import FontStyle, InlineSpan, Link

__all__ = [
    # Перечисления
    "ExtractedKind",
    "ListStyle",
    "ScriptPosition",
    # Геометрия
    "BBox",
    # Контекст и структура
    "SectionPath",
    "ListMarker",
    "TableCellRef",
    "TableContext",
    # Стили и ссылки
    "FontStyle",
    "Link",
    "InlineSpan",
    # Основные элементы
    "ExtractionProvenance",
    "ExtractedItem",
    # Опции и возможности
    "ExtractionOptions",
    "ExtractorCapability",
]
