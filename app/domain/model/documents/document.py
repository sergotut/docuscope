"""Доменная модель документа."""

from dataclasses import dataclass
from typing import NewType

from app.domain.exceptions import DomainValidationError

__all__ = ["DocumentId", "Document"]

DocumentId = NewType("DocumentId", str)
DocumentId.__doc__ = (
    "Строгий тип идентификатора документа (например, UUID или произвольная "
    "строка)."
)


@dataclass(frozen=True, slots=True)
class Document:
    """Документ с заголовком и содержимым.

    Attributes:
        id (DocumentId): Идентификатор документа.
        title (str): Заголовок документа. Не может быть пустым.
        content (str): Текстовое содержимое документа. Не может быть пустым.
    """

    id: DocumentId
    title: str
    content: str

    def __post_init__(self) -> None:
        """Проверяет валидность полей.

        Raises:
            DomainValidationError: Если title или content пусты.
        """
        if not self.title.strip():
            raise DomainValidationError("title не может быть пустым")
        if not self.content.strip():
            raise DomainValidationError("content не может быть пустым")
