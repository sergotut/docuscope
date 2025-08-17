"""Доменные модели имен и валидация сущностей в векторном хранилище."""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern
from typing import Final

from app.domain.model.validation import validate_name

__all__ = ["FieldName"]

# Разрешённые символы: латиница, цифры, _, -
_ALLOWED_NAME_RE: Final[Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]+$")
_MAX_LEN: Final[int] = 128


@dataclass(frozen=True, slots=True)
class FieldName:
    """Имя поля payload/документа для фильтров и индексов.

    Attributes:
        value (str): Строковое имя поля (валидированное).
    """

    value: str

    def __post_init__(self) -> None:
        """Валидирует значение при создании."""
        object.__setattr__(
            self,
            "value",
            _validate_name(
                self.value,
                allowed_re=_ALLOWED_NAME_RE,
                max_len=_MAX_LEN,
                kind="Field"
            )
        )

    def __str__(self) -> str:
        """Возвращает строковое представление.

        Returns:
            str: Имя поля.
        """
        return self.value
