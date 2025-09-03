"""Общая иерархия ошибок сервиса «Документоскоп»."""

from __future__ import annotations

__all__ = [
    "DocuscopeError",
    "StorageError",
    "VectorStoreError",
    "DomainValidationError",
    "DocumentConversionError",
    "DocumentExtractionError",
    "ExtractionTimeoutError",
    "UnsupportedExtractionFormatError",
    "CorruptedDocumentError",
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


class DocumentExtractionError(DocuscopeError):
    """Базовое исключение для ошибок экстракции контента из документов.

    Включает все типы ошибок, возникающие при извлечении структурированного
    контента из документов: технические сбои парсинга, проблемы доступа
    к источнику, ошибки декодирования и другие проблемы процесса экстракции.
    """


class ExtractionTimeoutError(DocumentExtractionError):
    """Ошибка превышения времени ожидания при экстракции документа.

    Возникает когда процесс извлечения контента превышает установленные
    временные лимиты. Может указывать на слишком большой документ,
    проблемы производительности или зависшие операции.
    """


class UnsupportedExtractionFormatError(DocumentExtractionError):
    """Ошибка неподдерживаемого формата документа для экстракции.

    Возникает когда экстрактор не может обработать документ указанного
    типа или формата, либо когда формат повреждён или нестандартен.
    """


class CorruptedDocumentError(DocumentExtractionError):
    """Ошибка повреждённого или нечитаемого документа.

    Возникает когда структура документа нарушена, файл повреждён
    или содержит данные, которые невозможно корректно интерпретировать.
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
