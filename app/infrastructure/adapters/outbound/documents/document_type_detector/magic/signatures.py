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
    limit = 16384 if scan_limit is None else max(0, int(scan_limit))
