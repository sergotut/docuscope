"""Доменная модель фрагмента документа (chunk)."""

from dataclasses import dataclass
from typing import NewType

from app.domain.exceptions import DomainValidationError
from app.domain.model.documents import DocumentId

__all__ = ["ChunkId", "Chunk"]

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
        if not self.doc_id.strip():
            raise DomainValidationError("doc_id не может быть пустым")
        if not self.text.strip():
            raise DomainValidationError("text не может быть пустым")
        if self.order < 0:
            raise DomainValidationError("order должен быть неотрицательным")
