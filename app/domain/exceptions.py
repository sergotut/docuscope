"""Общая иерархия ошибок сервиса «Документоскоп»."""

from __future__ import annotations

__all__ = [
    "DocuscopeError",
    "StorageError",
    "VectorStoreError",
    "DomainValidationError",
    "DocumentConversionError",
    "TokenError",
    "DocumentIngestError",
    "FileSizeTooLargeError",
    "UnsupportedDocumentTypeError",
]


class DocuscopeError(Exception):
    """Базовое исключение Документоскопа."""


class StorageError(DocuscopeError):
    """Ошибки, возникающие при работе с файловым хранилищем."""


class VectorStoreError(DocuscopeError):
    """Ошибки, возникающие при операциях с векторным хранилищем."""


class DomainValidationError(DocuscopeError):
    """Ошибки валидации доменных моделей и их аргументов."""


class DocumentConversionError(DocuscopeError):
    """Ошибки, возникающие при конвертации документов между форматами.

    Включает технические сбои конвертации, неподдерживаемые форматы,
    повреждённые исходные файлы и другие проблемы процесса конвертации.
    """


class TokenError(DomainValidationError):
    """Ошибки, связанные с токенами и их подсчётом."""


class DocumentIngestError(DocuscopeError):
    """Базовое исключение для ошибок инжеста документов.

    Включает все типы ошибок, возникающие при приёме, обработке
    и сохранении документов в системе.
    """


class FileSizeTooLargeError(DocumentIngestError):
    """Ошибка превышения максимального размера файла.

    Возникает когда загружаемый документ превышает установленные
    лимиты размера файла для обработки системой.
    """


class UnsupportedDocumentTypeError(DocumentIngestError):
    """Ошибка неподдерживаемого типа документа.

    Возникает когда тип загружаемого документа не входит в список
    разрешённых для обработки типов или не может быть определён.
    """
