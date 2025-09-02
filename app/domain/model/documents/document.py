"""Доменная модель документа и метаданные хранения."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from app.domain.exceptions import DomainValidationError
from app.domain.model.collections import CollectionName
from app.domain.model.shared import ObjectName
from app.domain.model.validation.uuid import validate_uuid_like

__all__ = [
    "DocumentId",
    "DocumentBase",
    "Document",
    "DocumentMeta",
    "to_document_id",
    "check_document_id",
    "to_original_name",
    "check_original_name",
]

DocumentId = NewType("DocumentId", str)
DocumentId.__doc__ = (
    "Строгий тип идентификатора документа (UUID-like строка, допускается с дефисами)."
)

OriginalName = NewType("OriginalName", str)
OriginalName.__doc__ = (
    "Строгий тип оригинального имени, полученного от пользователя при загрузке."
)


@dataclass(frozen=True, slots=True)
class DocumentBase:
    """Общая часть документа: идентификатор и опциональный заголовок.

    Attributes:
        id (DocumentId): Идентификатор документа.
        title (str | None): Заголовок (может отсутствовать).
    """

    id: DocumentId
    title: str | None

    def __post_init__(self) -> None:
        """Проверяет валидность идентификатора документа."""
        check_document_id(self.id)


@dataclass(frozen=True, slots=True)
class Document(DocumentBase):
    """Документ с заголовком и содержимым.

    Attributes:
        id (DocumentId): Идентификатор документа.
        title (str): Заголовок документа.
        content (str): Текстовое содержимое документа. Не может быть пустым.
    """

    content: str

    def __post_init__(self) -> None:
        """Проверяет валидность заголовка и содержимого.

        Raises:
            DomainValidationError: Если content пустой.
        """
        if not self.content.strip():
            raise DomainValidationError("content не может быть пустым")


@dataclass(frozen=True, slots=True)
class DocumentMeta(DocumentBase):
    """Метаданные документа для SQL/объектного хранения (без контента).

    Attributes:
        id (DocumentId): Идентификатор документа.
        title (str | None): Заголовок, если есть.
        collection (CollectionName): Коллекция-владелец.
        object_name (ObjectName): Ключ в объектном хранилище.
        original_filename (OriginalName): Имя файла от пользователя при загрузке.
        mime (str): MIME-тип исходного файла.
        size_bytes (int): Размер исходного файла в байтах.
        content_sha256 (str): Контент-хеш (идемпотентность/аудит).
        created_at (datetime): Время записи.
    """

    collection: CollectionName
    object_name: ObjectName
    original_filename: OriginalName
    mime: str
    size_bytes: int
    content_sha256: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Проверяет обязательные поля и корректность временной метки.

        Raises:
            ValueError: Если size_bytes отрицательный или content_sha256 слишком
                короткий.
        """
        check_original_name(self.original_filename)

        if self.size_bytes < 0:
            raise ValueError("size_bytes должен быть >= 0")

        if not self.content_sha256 or len(self.content_sha256) < 16:
            raise ValueError("content_sha256 выглядит недействительным")


def check_document_id(value: str | DocumentId) -> DocumentId:
    """Валидирует и приводит к типу DocumentId.

    Args:
        value (str | DocumentId): Строка UUID или уже типизированное значение.

    Returns:
        DocumentId: Валидированное значение.

    Raises:
        DomainValidationError: Если строка не UUID-подобна.
    """
    s = str(value)
    validate_uuid_like(s, kind="DocumentId")
    return DocumentId(s)


def to_document_id(value: str) -> DocumentId:
    """Преобразует строку в DocumentId с валидацией.

    Синоним check_document_id для выразительности в местах, где важно
    подчеркнуть преобразование типов.

    Args:
        value (str): Строковое представление UUID.

    Returns:
        DocumentId: Валидированное значение.

    Raises:
        DomainValidationError: Если строка не UUID-подобна.
    """
    return check_document_id(value)


def check_original_name(value: str | OriginalName) -> OriginalName:
    """Валидирует и приводит к типу OriginalName.

    Args:
        value (str | OriginalName): Оригинальное имя файла от пользователя.

    Returns:
        OriginalName: Нормализованная (обрезанная) строка.

    Raises:
        DomainValidationError: Если имя пустое после обрезки.
    """
    s = str(value).strip()
    if not s:
        raise DomainValidationError("Original name must not be empty.")
    return OriginalName(s)


def to_original_name(value: str) -> OriginalName:
    """Преобразует строку в OriginalName с валидацией.

    Args:
        value (str): Оригинальное имя файла.

    Returns:
        OriginalName: Валидированное значение.

    Raises:
        DomainValidationError: Если имя пустое.
    """
    return check_original_name(value)
