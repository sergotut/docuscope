"""Перечисления (Enum) и политика допуска типов документов.

Содержит укрупнённые семейства, строгие типы и правила допуска.
"""

from __future__ import annotations

from enum import Enum
from typing import Final

__all__ = [
    "DocumentFamily",
    "DocumentType",
    "Permission",
    "DOCUMENT_FAMILY_BY_TYPE",
    "ALLOWED_DOCUMENT_TYPES",
    "family_of",
    "is_allowed_type",
    "permission_of",
]


class DocumentFamily(str, Enum):
    """Укрупнённые семейства документов.

    Attributes:
        WORD: Текстовые документы Microsoft Word.
        EXCEL: Таблицы Microsoft Excel.
        PDF: Документы PDF.
        IMAGE: Растровые изображения.
        UNKNOWN: Неизвестное или нераспознанное семейство.
    """

    WORD = "word"
    EXCEL = "excel"
    PDF = "pdf"
    IMAGE = "image"
    UNKNOWN = "unknown"


class DocumentType(str, Enum):
    """Строгие типы документов (детализированные).

    Изображения указываются конкретным контейнером.

    Attributes:
        WORD_DOC: Формат Word .doc (старый бинарный).
        WORD_DOCX: Формат Word .docx.
        EXCEL_XLS: Формат Excel .xls (старый бинарный).
        EXCEL_XLSX: Формат Excel .xlsx.
        PDF: PDF.
        IMAGE_JPEG: Растровое изображение JPEG.
        IMAGE_PNG: Растровое изображение PNG.
        IMAGE_TIFF: Растровое изображение TIFF.
        IMAGE_BMP: Растровое изображение BMP.
        IMAGE_GIF: Растровое изображение GIF.
        IMAGE_WEBP: Растровое изображение WebP.
        UNKNOWN: Неизвестный или нераспознанный тип.
    """

    WORD_DOC = "word_doc"
    WORD_DOCX = "word_docx"
    EXCEL_XLS = "excel_xls"
    EXCEL_XLSX = "excel_xlsx"
    PDF = "pdf"

    IMAGE_JPEG = "image_jpeg"
    IMAGE_PNG = "image_png"
    IMAGE_TIFF = "image_tiff"
    IMAGE_BMP = "image_bmp"
    IMAGE_GIF = "image_gif"
    IMAGE_WEBP = "image_webp"

    UNKNOWN = "unknown"


class Permission(str, Enum):
    """Решение о допуске документа согласно политике.

    Attributes:
        ALLOWED: Тип разрешён политикой.
        FORBIDDEN: Тип запрещён политикой.
    """

    ALLOWED = "allowed"
    FORBIDDEN = "forbidden"


# Отображение строгого типа документа и его семейства.
DOCUMENT_FAMILY_BY_TYPE: Final[dict[DocumentType, DocumentFamily]] = {
    DocumentType.WORD_DOC: DocumentFamily.WORD,
    DocumentType.WORD_DOCX: DocumentFamily.WORD,
    DocumentType.EXCEL_XLS: DocumentFamily.EXCEL,
    DocumentType.EXCEL_XLSX: DocumentFamily.EXCEL,
    DocumentType.PDF: DocumentFamily.PDF,
    DocumentType.IMAGE_JPEG: DocumentFamily.IMAGE,
    DocumentType.IMAGE_PNG: DocumentFamily.IMAGE,
    DocumentType.IMAGE_TIFF: DocumentFamily.IMAGE,
    DocumentType.IMAGE_BMP: DocumentFamily.IMAGE,
    DocumentType.IMAGE_GIF: DocumentFamily.IMAGE,
    DocumentType.IMAGE_WEBP: DocumentFamily.IMAGE,
}

# Допустимые типы документов.
ALLOWED_DOCUMENT_TYPES: Final[frozenset[DocumentType]] = frozenset(
    {
        DocumentType.WORD_DOC,
        DocumentType.WORD_DOCX,
        DocumentType.EXCEL_XLS,
        DocumentType.EXCEL_XLSX,
        DocumentType.PDF,
        DocumentType.IMAGE_JPEG,
        DocumentType.IMAGE_PNG,
        DocumentType.IMAGE_TIFF,
        DocumentType.IMAGE_BMP,
        DocumentType.IMAGE_GIF,
        DocumentType.IMAGE_WEBP,
    }
)


def family_of(type_: DocumentType) -> DocumentFamily:
    """Возвращает семейство для строгого типа.

    Args:
        type_: Строгий тип документа.

    Returns:
        Соответствующее семейство документа. Если тип не распознан, возвращается
        DocumentFamily.UNKNOWN.
    """
    return DOCUMENT_FAMILY_BY_TYPE.get(type_, DocumentFamily.UNKNOWN)


def is_allowed_type(type_: DocumentType) -> bool:
    """Проверяет допуск строгого типа согласно политике.

    Args:
        type_: Строгий тип документа.

    Returns:
        True, если тип разрешён политикой; иначе False.
    """
    return type_ in ALLOWED_DOCUMENT_TYPES


def permission_of(type_: DocumentType) -> Permission:
    """Возвращает решение о допуске для строгого типа.

    Является тонкой обёрткой над is_allowed_type.

    Args:
        type_: Строгий тип документа.

    Returns:
        Permission.ALLOWED для разрешённых типов, иначе Permission.FORBIDDEN.
    """
    return (
        Permission.ALLOWED
        if type_ in ALLOWED_DOCUMENT_TYPES
        else Permission.FORBIDDEN
    )
