"""Доменные модели имен и валидация сущностей в векторном хранилище.

Определяет типы для имён коллекций и полей, а также общую функцию проверки
строк на пустоту, длину и допустимые символы.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern
from typing import Final

__all__ = ["CollectionName", "FieldName"]

# Разрешённые символы: латиница, цифры, ., _, -
_ALLOWED_NAME_RE: Final[Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]+$")
_MAX_LEN: Final[int] = 128


def _validate_name(value: str, *, kind: str) -> str:
    """Проверяет строку на пустоту, длину и допустимые символы.

    Args:
        value (str): Исходная строка.
        kind (str): Тип сущности для сообщений об ошибках.

    Returns:
        str: Нормализованная строка (обрезанные пробелы).

    Raises:
        ValueError: Если строка пустая, слишком длинная или содержит
            недопустимые символы.
    """
    v = value.strip()

    if not v:
        msg = f"{kind} не может быть пустым."
        raise ValueError(msg)

    if len(v) > _MAX_LEN:
        msg = f"{kind} превышает допустимую длину {_MAX_LEN}."
        raise ValueError(msg)

    if not _ALLOWED_NAME_RE.match(v):
        msg = (
            f"{kind} содержит недопустимые символы. "
            "Разрешены: латиница, цифры, точка, подчёркивание, дефис."
        )
        raise ValueError(msg)

    return v


@dataclass(frozen=True, slots=True)
class CollectionName:
    """Имя коллекции (индекса/namespace) в векторном хранилище.

    Attributes:
        value (str): Строковое имя коллекции (валидированное).
    """

    value: str

    def __post_init__(self) -> None:
        """Валидирует значение при создании."""
        object.__setattr__(
            self,
            "value",
            _validate_name(self.value, kind="Collection")
        )

    def __str__(self) -> str:
        """Возвращает строковое представление.

        Returns:
            str: Имя коллекции.
        """
        return self.value


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
            _validate_name(self.value, kind="Field")
        )

    def __str__(self) -> str:
        """Возвращает строковое представление.

        Returns:
            str: Имя поля.
        """
        return self.value
