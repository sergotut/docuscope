"""Доменная модель фрагмента документа (chunk)."""

from dataclasses import dataclass
from typing import NewType

from app.domain.exceptions import DomainValidationError
from app.domain.model.documents import (
    DocumentId,
    check_document_id,
)
from app.domain.model.validation.uuid import validate_uuid_like

__all__ = ["ChunkId", "Chunk", "to_chunk_id", "check_chunk_id"]

ChunkId = NewType("ChunkId", str)
ChunkId.__doc__ = (
    "Строгий тип идентификатора фрагмента документа (chunk). "
    "Представляет собой строковый идентификатор."
)


@dataclass(frozen=True, slots=True)
class Chunk:
    """Фрагмент документа.

    Attributes:
        id (ChunkId): Идентификатор фрагмента.
        doc_id (DocumentId): Идентификатор документа, к которому относится
            фрагмент. Не может быть пустым.
        text (str): Текст фрагмента. Не может быть пустым.
        order (int): Порядковый номер фрагмента в документе. Должен быть
            неотрицательным.
    """

    id: ChunkId
    doc_id: DocumentId
    text: str
    order: int

    def __post_init__(self) -> None:
        """Проверяет валидность полей.

        Raises:
            DomainValidationError: Если doc_id или text пусты, либо order < 0.
        """
        check_chunk_id(self.id)
        check_document_id(self.doc_id)

        if not self.text.strip():
            raise DomainValidationError("text не может быть пустым")
        if self.order < 0:
            raise DomainValidationError("order должен быть неотрицательным")


def check_chunk_id(value: str | ChunkId) -> ChunkId:
    """Валидирует и приводит к типу ChunkId."""
    s = str(value)
    validate_uuid_like(s, kind="ChunkId")
    return ChunkId(s)


def to_chunk_id(value: str) -> ChunkId:
    """Преобразует строку в ChunkId с валидацией."""
    return check_chunk_id(value)
