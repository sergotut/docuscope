"""Сигнатуры форматов и правила распознавания по первым байтам.

Безопасность: нет регулярных выражений и декомпрессии. Поиск идёт только
по срезу байтов в памяти.
"""

from __future__ import annotations

from typing import Callable, Final, NamedTuple

import structlog

try:  # опционально усиливаем детекцию, если зависимость доступна
    import magic  # type: ignore
except Exception:  # pragma: no cover - отсутствие libmagic допустимо
    magic = None  # type: ignore

from app.domain.model.documents.types import DocumentType

from .utils import find_any

__all__ = ["sniff_magic", "has_ole_signature"]

logger = structlog.get_logger(__name__)

# Константы сигнатур (используем bytes.startswith)
PDF_MAGIC: Final = b"%PDF-"
JPEG_MAGIC: Final = b"\xff\xd8\xff"
PNG_MAGIC: Final = b"\x89PNG\r\n\x1a\n"
GIF_MAGICS: Final = (b"GIF87a", b"GIF89a")
BMP_MAGIC: Final = b"BM"
TIFF_MAGICS: Final = (b"II*\x00", b"MM\x00*")
RIFF_MAGIC: Final = b"RIFF"
WEBP_TAG: Final = b"WEBP"
ZIP_MAGIC: Final = b"PK\x03\x04"
OLE_MAGIC: Final = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


class _MagicRule(NamedTuple):
    """Правило сопоставления по сигнатуре.

    Attributes:
        check (Callable[[bytes, int], bool]): Предикат (buf, limit) -> bool.
        dtype (DocumentType | None): Определённый тип документа или None.
        mime (str | None): MIME-тип или None.
        note (str | None): Дополнительная заметка к результату.
    """

    check: Callable[[bytes, int], bool]
    dtype: DocumentType | None
    mime: str | None
    note: str | None = None


def _is_pdf(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(PDF_MAGIC)


def _is_jpeg(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(JPEG_MAGIC)


def _is_png(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(PNG_MAGIC)


def _is_gif(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(GIF_MAGICS)


def _is_bmp(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(BMP_MAGIC)


def _is_tiff(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(TIFF_MAGICS)


def _is_webp(h: bytes, _limit: int) -> bool:
    """Проверяет шаблон RIFF....WEBP (offset 8..11).

    Args:
        h (bytes): Буфер первых байт файла.
        _limit (int): Лимит для внутренних поисков (не используется).

    Returns:
        bool: True, если буфер соответствует формату WebP.
    """
    return h.startswith(RIFF_MAGIC) and h[8:12] == WEBP_TAG


def _is_docx(h: bytes, limit: int) -> bool:
    """Определяет DOCX по ZIP и маркерам директорий в первых байтах.

    Args:
        h (bytes): Буфер первых байт файла.
        limit (int): Лимит для поиска внутренних маркеров.

    Returns:
        bool: Признак наличия признаков DOCX.
    """
    return h.startswith(ZIP_MAGIC) and find_any(
        h,
        (b"word/", b"word/document.xml"),
        limit=limit,
    )


def _is_xlsx(h: bytes, limit: int) -> bool:
    """Определяет XLSX по ZIP и маркерам директорий в первых байтах.

    Args:
        h (bytes): Буфер первых байт файла.
        limit (int): Лимит для поиска внутренних маркеров.

    Returns:
        bool: Признак наличия признаков XLSX.
    """
    return h.startswith(ZIP_MAGIC) and find_any(
        h,
        (b"xl/", b"xl/workbook.xml"),
        limit=limit,
    )


def _is_zip_unknown_ooxml(h: bytes, _limit: int) -> bool:
    """Определяет ZIP без явных маркеров OOXML в первых байтах.

    Args:
        h (bytes): Буфер первых байт файла.
        _limit (int): Лимит для внутренних поисков (не используется).

    Returns:
        bool: True, если начало файла соответствует ZIP.
    """
    return h.startswith(ZIP_MAGIC)


def _is_ole(h: bytes, _limit: int) -> bool:  # noqa: D401
    return h.startswith(OLE_MAGIC)


_MAGIC_RULES: Final[tuple[_MagicRule, ...]] = (
    _MagicRule(_is_pdf, DocumentType.PDF, "application/pdf"),
    _MagicRule(_is_jpeg, DocumentType.IMAGE_JPEG, "image/jpeg"),
    _MagicRule(_is_png, DocumentType.IMAGE_PNG, "image/png"),
    _MagicRule(_is_gif, DocumentType.IMAGE_GIF, "image/gif"),
    _MagicRule(_is_bmp, DocumentType.IMAGE_BMP, "image/bmp"),
    _MagicRule(_is_tiff, DocumentType.IMAGE_TIFF, "image/tiff"),
    _MagicRule(_is_webp, DocumentType.IMAGE_WEBP, "image/webp"),
    _MagicRule(
        _is_docx,
        DocumentType.WORD_DOCX,
        ("application/" "vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ),
    _MagicRule(
        _is_xlsx,
        DocumentType.EXCEL_XLSX,
        ("application/" "vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ),
    _MagicRule(
        _is_zip_unknown_ooxml,
        None,
        "application/zip",
        "zip_container_unknown_ooxml",
    ),
    _MagicRule(_is_ole, None, "application/x-ole-storage", "ole_container"),
)


def sniff_magic(
    head: bytes,
    *,
    use_libmagic: bool = True,
    scan_limit: int | None = None,
) -> tuple[DocumentType | None, str | None, tuple[str, ...]]:
    """Проверяет буфер на известные сигнатуры форматов.

    Args:
        head (bytes): Первые N байт файла.
        use_libmagic (bool): Разрешать ли fallback к python-magic (если установлен).
        scan_limit (int | None): Лимит байт для внутренних поисков по контейнеру
            (например, word/…, xl/…). Если None, используется 16384.

    Returns:
        tuple[DocumentType | None, str | None, tuple[str, ...]]: Кортеж
        (тип документа или None, MIME или None, заметки).
    """
    if not head:
        return None, None, ()

    limit = scan_limit if scan_limit is not None else 16384
    notes: list[str] = []

    # Проверяем встроенные правила сигнатур
    for rule in _MAGIC_RULES:
        try:
            if rule.check(head, limit):
                if rule.note:
                    notes.append(rule.note)
                return rule.dtype, rule.mime, tuple(notes)
        except Exception as exc:
            logger.warning(
                "Ошибка проверки магической сигнатуры",
                rule_note=rule.note or "unknown",
                error=str(exc),
            )
            continue

    # Fallback к python-magic если доступен и разрешён
    if use_libmagic and magic is not None:
        try:
            mime_detected = magic.from_buffer(head, mime=True)
            if mime_detected and isinstance(mime_detected, str):
                notes.append("detected_by_libmagic")
                return None, mime_detected.lower(), tuple(notes)
        except Exception as exc:
            logger.debug(
                "Ошибка libmagic fallback",
                error=str(exc),
            )
            notes.append("libmagic_failed")

    # Ничего не найдено
    return None, None, tuple(notes)


def has_ole_signature(head: bytes) -> bool:
    """Проверяет наличие OLE (Compound Document) сигнатуры в буфере.

    Args:
        head (bytes): Первые N байт файла.

    Returns:
        bool: True, если найдена OLE сигнатура, иначе False.
    """
    return head.startswith(OLE_MAGIC) if head else False
