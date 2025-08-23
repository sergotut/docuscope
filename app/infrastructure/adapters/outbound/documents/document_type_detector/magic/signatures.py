"""Сигнатуры форматов и правила распознавания по первым байтам.

Безопасность: нет регулярных выражений и декомпрессии. Поиск идёт только
по срезу байтов в памяти.
"""

from __future__ import annotations

import structlog
from typing import Callable, Final, NamedTuple

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
JPEG_MAGIC: Final = b"\xFF\xD8\xFF"
PNG_MAGIC: Final = b"\x89PNG\r\n\x1A\n"
GIF_MAGICS: Final = (b"GIF87a", b"GIF89a")
BMP_MAGIC: Final = b"BM"
TIFF_MAGICS: Final = (b"II*\x00", b"MM\x00*")
RIFF_MAGIC: Final = b"RIFF"
WEBP_TAG: Final = b"WEBP"
ZIP_MAGIC: Final = b"PK\x03\x04"
OLE_MAGIC: Final = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"


class _MagicRule(NamedTuple):
    """Правило сопоставления по сигнатуре.

    Attributes:
        check (Callable[[bytes], bool]): Функция-предикат для проверки буфера.
        dtype (DocumentType | None): Определённый тип документа или None.
        mime (str | None): MIME-тип или None.
        note (str | None): Дополнительная заметка к результату.
    """
    check: Callable[[bytes], bool]
    dtype: DocumentType | None
    mime: str | None
    note: str | None = None


def _is_pdf(h: bytes) -> bool:  # noqa: D401 - простая проверка
    return h.startswith(PDF_MAGIC)


def _is_jpeg(h: bytes) -> bool:  # noqa: D401
    return h.startswith(JPEG_MAGIC)


def _is_png(h: bytes) -> bool:  # noqa: D401
    return h.startswith(PNG_MAGIC)


def _is_gif(h: bytes) -> bool:  # noqa: D401
    return h.startswith(GIF_MAGICS)


def _is_bmp(h: bytes) -> bool:  # noqa: D401
    return h.startswith(BMP_MAGIC)


def _is_tiff(h: bytes) -> bool:  # noqa: D401
    return h.startswith(TIFF_MAGICS)


def _is_webp(h: bytes) -> bool:
    """Проверяет шаблон RIFF....WEBP (offset 8..11).

    Args:
        h (bytes): Буфер первых байт файла.

    Returns:
        bool: True, если буфер соответствует формату WebP, иначе False.
    """
    return h.startswith(RIFF_MAGIC) and h[8:12] == WEBP_TAG


def _is_docx(h: bytes) -> bool:
    """Определяет DOCX по ZIP и маркерам директорий в первых байтах.

    Args:
        h (bytes): Буфер первых байт файла.

    Returns:
        bool: True, если в буфере обнаружены признаки DOCX, иначе False.
    """
    return h.startswith(ZIP_MAGIC) and find_any(
        h, (b"word/", b"word/document.xml")
    )


def _is_xlsx(h: bytes) -> bool:
    """Определяет XLSX по ZIP и маркерам директорий в первых байтах.

    Args:
        h (bytes): Буфер первых байт файла.

    Returns:
        bool: True, если в буфере обнаружены признаки XLSX; иначе False.
    """
    return h.startswith(ZIP_MAGIC) and find_any(
        h, (b"xl/", b"xl/workbook.xml")
    )


def _is_zip_unknown_ooxml(h: bytes) -> bool:
    """Определяет ZIP без явных маркеров OOXML в первых байтах.

    Args:
        h (bytes): Буфер первых байт файла.

    Returns:
        bool: True, если начало файла соответствует ZIP, иначе False.
    """
    return h.startswith(ZIP_MAGIC)


def _is_ole(h: bytes) -> bool:  # noqa: D401
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
        (
            "application/"
            "vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
    ),
    _MagicRule(
        _is_xlsx,
        DocumentType.EXCEL_XLSX,
        (
            "application/"
            "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
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
) -> tuple[DocumentType | None, str | None, tuple[str, ...]]:
    """Проверяет буфер на известные сигнатуры форматов.

    Args:
        head (bytes): Первые N байт файла.
        use_libmagic (bool): Разрешать ли fallback к python-magic (если установлен).

    Returns:
        tuple[DocumentType | None, str | None, tuple[str, ...]]: Кортеж
            (тип документа или None, MIME или None, заметки).
    """
    notes: list[str] = []
    for rule in _MAGIC_RULES:
        if rule.check(head):
            if rule.note:
                notes.append(rule.note)
            return (rule.dtype, rule.mime, tuple(notes))

    # Опционально: libmagic как подсказчик (если включено и доступно)
    if use_libmagic and magic is not None:  # pragma: no cover
        try:
            m = magic.Magic(mime=True)  # type: ignore[attr-defined]
            mime = m.from_buffer(head)  # type: ignore[assignment]
            return (None, str(mime), tuple(notes))
        except Exception:  # noqa: BLE001
            # Игнорируем сбои внешней либы, фиксируем стек для диагностики.
            logger.exception("libmagic failed in sniff_magic")

    return (None, None, tuple(notes))


def has_ole_signature(head: bytes) -> bool:
    """Проверяет начало буфера на сигнатуру OLE (legacy Office).

    Args:
        head (bytes): Первые N байт файла.

    Returns:
        bool: True, если буфер начинается с сигнатуры OLE, иначе False.
    """
    return head.startswith(OLE_MAGIC)
