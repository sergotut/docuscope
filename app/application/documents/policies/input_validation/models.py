"""Модели для валидации входа для документов."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DocumentInputConstraints",
]


@dataclass(frozen=True, slots=True)
class DocumentInputConstraints:
    """Ограничения прикладного уровня для входных документов.

    Attributes:
        max_document_size_mb (int): Максимально допустимый размер файла в МБ.
        max_filename_length (int): Максимальная длина имени файла.
    """

    max_document_size_mb: int
    max_filename_length: int
