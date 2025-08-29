"""Доменная модель документа и метаданные хранения."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from app.domain.exceptions import DomainValidationError
from app.domain.model.collections import CollectionName
from app.domain.model.shared import ObjectName

__all__ = [
    "DocumentId",
    "DocumentBase",
    "Document",
    "DocumentMeta",
]

DocumentId = NewType("DocumentId", str)
DocumentId.__doc__ = (
    "Строгий тип идентификатора документа (например, UUID или произвольная " "строка)."
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
        original_filename (str): Имя файла от пользователя при загрузке.
        mime (str): MIME-тип исходного файла.
        size_bytes (int): Размер исходного файла в байтах.
        content_sha256 (str): Контент-хеш (идемпотентность/аудит).
        created_at (datetime): Время записи.
    """

    collection: CollectionName
    object_name: ObjectName
    original_filename: str
    mime: str
    size_bytes: int
    content_sha256: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Проверяет обязательные поля и корректность временной метки.

        Raises:
            ValueError: Если original_filename пустой, size_bytes отрицательный,
                content_sha256 слишком короткий или created_at без таймзоны.
        """
        if not self.original_filename.strip():
            raise ValueError("original_filename не может быть пустым")

        if self.size_bytes < 0:
            raise ValueError("size_bytes должен быть >= 0")

        if not self.content_sha256 or len(self.content_sha256) < 16:
            raise ValueError("content_sha256 выглядит недействительным")
