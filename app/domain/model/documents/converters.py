"""Конвертеры между расширениями и MIME-типами в DocumentType.

Содержит функции для нормализации входных данных при определении типа документа.
"""

from __future__ import annotations

from typing import Final

from .types import DocumentType

__all__ = ["from_extension", "from_mimetype"]

_EXT_TO_TYPE: Final[dict[str, DocumentType]] = {
    # Word
    "doc": DocumentType.WORD_DOC,
    "docx": DocumentType.WORD_DOCX,
    # Excel
    "xls": DocumentType.EXCEL_XLS,
    "xlsx": DocumentType.EXCEL_XLSX,
    # PDF
    "pdf": DocumentType.PDF,
    # Images
    "jpg": DocumentType.IMAGE_JPEG,
    "jpeg": DocumentType.IMAGE_JPEG,
    "png": DocumentType.IMAGE_PNG,
    "tif": DocumentType.IMAGE_TIFF,
    "tiff": DocumentType.IMAGE_TIFF,
    "bmp": DocumentType.IMAGE_BMP,
    "gif": DocumentType.IMAGE_GIF,
    "webp": DocumentType.IMAGE_WEBP,
}

_MIMETYPE_TO_TYPE: Final[dict[str, DocumentType]] = {
    # Word
    "application/msword": DocumentType.WORD_DOC,
    (
        "application/" "vnd.openxmlformats-officedocument.wordprocessingml.document"
    ): DocumentType.WORD_DOCX,
    # Excel
    "application/vnd.ms-excel": DocumentType.EXCEL_XLS,
    (
        "application/" "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ): DocumentType.EXCEL_XLSX,
    # PDF
    "application/pdf": DocumentType.PDF,
    # Images
    "image/jpeg": DocumentType.IMAGE_JPEG,
    "image/png": DocumentType.IMAGE_PNG,
    "image/tiff": DocumentType.IMAGE_TIFF,
    "image/bmp": DocumentType.IMAGE_BMP,
    "image/gif": DocumentType.IMAGE_GIF,
    "image/webp": DocumentType.IMAGE_WEBP,
}

_TYPE_TO_MIMETYPE: Final[dict[DocumentType, str]] = {
    # Word
    DocumentType.WORD_DOC: "application/msword",
    DocumentType.WORD_DOCX: (
        "application/" "vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
    # Excel
    DocumentType.EXCEL_XLS: "application/vnd.ms-excel",
    DocumentType.EXCEL_XLSX: (
        "application/" "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ),
    # PDF
    DocumentType.PDF: "application/pdf",
    # Images
    DocumentType.IMAGE_JPEG: "image/jpeg",
    DocumentType.IMAGE_PNG: "image/png",
    DocumentType.IMAGE_TIFF: "image/tiff",
    DocumentType.IMAGE_BMP: "image/bmp",
    DocumentType.IMAGE_GIF: "image/gif",
    DocumentType.IMAGE_WEBP: "image/webp",
}


def from_extension(extension: str) -> DocumentType:
    """Определяет DocumentType по расширению файла.

    Расширение можно передавать с точкой или без (.docx или docx). Регистр
    символов не важен. Неизвестные расширения возвращают DocumentType.UNKNOWN.

    Args:
        extension (str): Расширение файла с точкой или без.

    Returns:
        DocumentType: Соответствующий тип или DocumentType.UNKNOWN.
    """
    if not extension:
        return DocumentType.UNKNOWN

    ext = extension.lower().lstrip(".")

    return _EXT_TO_TYPE.get(ext, DocumentType.UNKNOWN)


def from_mimetype(mimetype: str) -> DocumentType:
    """Определяет DocumentType по MIME-типу.

    Регистр символов не важен. Неизвестные значения возвращают
    DocumentType.UNKNOWN.

    Args:
        mimetype (str): MIME-тип, например application/pdf.

    Returns:
        DocumentType: Соответствующий тип или DocumentType.UNKNOWN.
    """
    if not mimetype:
        return DocumentType.UNKNOWN

    m = mimetype.strip().lower().split(";", 1)[0]

    return _MIMETYPE_TO_TYPE.get(m, DocumentType.UNKNOWN)


def mime_of(doc_type: DocumentType) -> str | None:
    """Возвращает каноничный MIME для заданного DocumentType.

    Args:
        doc_type (DocumentType): Строгий тип документа.

    Returns:
        str | None: Каноничный MIME-тип или None, если соответствие не задано.
    """
    return _TYPE_TO_MIMETYPE.get(doc_type)
