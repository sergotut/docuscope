"""Доменные модели коллекции: CollectionName и CollectionMeta.

Содержит:
- типизированное имя коллекции с единой валидацией;
- минимальную мета-модель коллекции под политику TTL и «одна загрузка».
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from re import Pattern
from typing import Final, Literal

from app.domain.model.validation import validate_name

__all__ = [
    "CollectionName",
    "CollectionMeta",
    "CollectionStatus",
]

# Разрешённые символы: латиница, цифры, точка, подчёркивание, дефис.
_ALLOWED_NAME_RE: Final[Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]+$")
_MAX_LEN: Final[int] = 128

CollectionStatus = Literal["new", "uploaded", "expired", "failed"]


@dataclass(frozen=True, slots=True)
class CollectionName:
    """Имя коллекции/namespace для любых хранилищ.

    Attributes:
        value (str): Строковое имя коллекции (валидированное).
    """

    value: str

    def __post_init__(self) -> None:
        """Валидирует значение при создании."""
        object.__setattr__(
            self,
            "value",
            validate_name(
                self.value,
                allowed_re=_ALLOWED_NAME_RE,
                max_len=_MAX_LEN,
                kind="Collection",
            ),
        )

    def __str__(self) -> str:
        """Возвращает строковое представление.

        Returns:
            str: Имя коллекции.
        """
        return self.value


@dataclass(frozen=True, slots=True)
class CollectionMeta:
    """Минимальная мета коллекции под политику TTL и «одна загрузка».

    Никаких чанков/контента — только контрольные метаданные.

    Attributes:
        name (CollectionName): Имя коллекции.
        created_at (datetime): Время создания.
        expire_at (datetime): Время истечения TTL.
        sealed_at (datetime | None): Момент загрузки.
        status (CollectionStatus): Статус коллекции.
        version (int): Версия.
    """

    name: CollectionName
    created_at: datetime
    expire_at: datetime
    sealed_at: datetime | None
    status: CollectionStatus
    version: int
