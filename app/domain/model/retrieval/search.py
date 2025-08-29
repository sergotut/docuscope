"""Доменные модели для поиска: оценённый фрагмент и запрос.

Содержит:
- :class:ScoredChunk — фрагмент документа с числовым скором (больше — лучше).
- :class:Query — текст запроса с опциональной областью поиска по document_id.
"""

import math
from dataclasses import dataclass

from app.domain.exceptions import DomainValidationError
from app.domain.model.documents import Chunk, DocumentId

__all__ = ["ScoredChunk", "Query"]


@dataclass(frozen=True, slots=True)
class ScoredChunk:
    """Фрагмент документа с оценкой релевантности.

    Attributes:
        chunk (Chunk): Фрагмент документа.
        score (float): Числовая оценка релевантности. Требуется конечное значение
            (не NaN и не бесконечность). Диапазон не фиксирован и
            зависит от алгоритма.
    """

    chunk: Chunk
    score: float

    def __post_init__(self) -> None:
        """Проверяет валидность score.

        Raises:
            DomainValidationError: Если score не является конечным числом.
        """
        if not math.isfinite(self.score):
            msg = f"score должен быть конечным числом, получено: {self.score!r}"
            raise DomainValidationError(msg)


@dataclass(frozen=True, slots=True)
class Query:
    """Текстовый запрос на поиск.

    Attributes:
        text (str): Текст запроса. Не может быть пустым или состоять из пробелов.
        scope_doc_id (DocumentId): Обязательный идентификатор документа для ограничения
            области поиска.
    """

    text: str
    scope_doc_id: DocumentId

    def __post_init__(self) -> None:
        """Проверяет валидность полей.

        Raises:
            DomainValidationError: Если text или scope_doc_id пусты.
        """
        if not self.text.strip():
            raise DomainValidationError("text запроса не может быть пустым")
        if not self.scope_doc_id.strip():
            raise DomainValidationError(
                "scope_doc_id обязателен и не может быть пустым"
            )
