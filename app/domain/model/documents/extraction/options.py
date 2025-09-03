"""Опции и возможности экстракции документов."""

from __future__ import annotations

from dataclasses import dataclass

from .enums import ExtractedKind

__all__ = [
    "ExtractionOptions",
    "ExtractorCapability",
]


@dataclass(frozen=True, slots=True)
class ExtractionOptions:
    """Опции экстракции, влияющие на полноту, скорость и нормализацию.

    Конфигурирует поведение экстрактора для баланса между качеством результата и
    производительностью. Позволяет настроить включение различных типов контента и
    применение нормализующих преобразований.

    Attributes:
        include_headers_footers (bool): Включать колонтитулы в результат.
        include_footnotes (bool): Включать нижние сноски.
        include_endnotes (bool): Включать концевые сноски.
        include_captions (bool): Включать подписи к таблицам и рисункам.
        include_tables (bool): Экстрагировать содержимое таблиц.
        flatten_tables_as_rows (bool): Представлять таблицы строками, а не ячейками.
        parse_list_markers (bool): Определять маркеры списков и уровни вложенности.
        compute_section_hierarchy (bool): Вычислять иерархию разделов и нумерацию.
        detect_headings_by_style (bool): Использовать эвристику
            "шрифт/размер -> заголовок".
        detect_columns (bool): Детектировать колоночную вёрстку в PDF.
        join_hyphenated (bool): Склеивать слова с переносами на разрывах строк.
        normalize_whitespace (bool): Очищать избыточные пробелы и переводы строк.
        deduplicate (bool): Пытаться удалять очевидные дубликаты блоков.
        page_from (int | None): Начальная страница для обработки (с 1).
        page_to (int | None): Конечная страница для обработки (включительно).
        max_pages (int | None): Максимальное количество страниц для обработки.
        max_items (int | None): Лимит элементов (поток прерывается при достижении).
        ocr_fallback (bool): Применять OCR для "пустых" страниц PDF.
        language_hint (str | None): Подсказка о языке документа для улучшения качества.
    """

    include_headers_footers: bool = False
    include_footnotes: bool = True
    include_endnotes: bool = True
    include_captions: bool = True
    include_tables: bool = True
    flatten_tables_as_rows: bool = True

    parse_list_markers: bool = True
    compute_section_hierarchy: bool = True
    detect_headings_by_style: bool = True
    detect_columns: bool = True

    join_hyphenated: bool = True
    normalize_whitespace: bool = True
    deduplicate: bool = True

    page_from: int | None = None
    page_to: int | None = None
    max_pages: int | None = None
    max_items: int | None = None

    ocr_fallback: bool = False
    language_hint: str | None = None


@dataclass(frozen=True, slots=True)
class ExtractorCapability:
    """Возможности конкретной реализации порта экстракции.

    Описывает функциональные возможности экстрактора для правильного выбора адаптера и
    настройки ожиданий от результата.

    Attributes:
        provides_spans (bool): Способность выдавать InlineSpan с детальными стилями.
        provides_bbox (bool): Способность определять координаты и геометрию элементов.
        provides_table_ctx (bool): Способность извлекать контекст таблиц.
        provides_sections (bool): Способность определять иерархию разделов.
        preserves_order (bool): Гарантия сохранения порядка чтения элементов.
        supported_kinds (tuple[ExtractedKind, ...]): Типы элементов, которые может
            извлечь экстрактор.
    """

    provides_spans: bool = False
    provides_bbox: bool = False
    provides_table_ctx: bool = False
    provides_sections: bool = False
    preserves_order: bool = True
    supported_kinds: tuple[ExtractedKind, ...] = ()
