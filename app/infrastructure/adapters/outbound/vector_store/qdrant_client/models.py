"""Провайдер-специфичные value-объекты для Qdrant.

Содержит декларации индексов payload и их конфигурации. Эти модели
используются на уровне инфраструктуры (миграции/инициализация индексов)
и не попадают в доменный слой.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

from app.domain.model.vector_store import FieldName

__all__ = [
    "QdrantDistance",
    "QdrantTextIndexConfig",
    "QdrantKeywordIndexSpec",
    "QdrantTextIndexSpec",
]


class QdrantDistance(str, Enum):
    """Метрика расстояния для dense-векторов в Qdrant.

    Values:
        COSINE (str): Косинусная метрика.
        DOT (str): Скалярное произведение.
        EUCLID (str): Евклидово расстояние.
    """

    COSINE = "cosine"
    DOT = "dot"
    EUCLID = "euclid"


@dataclass(frozen=True, slots=True)
class QdrantTextIndexConfig:
    """Конфигурация текстового индекса.

    Attributes:
        tokenizer (Literal["word", "space", "prefix"]): Тип токенизатора.
        min_token_len (int): Минимальная длина токена, не меньше 1.
        max_token_len (int): Максимальная длина токена, не меньше
            min_token_len.
        lowercase (bool): Приводить ли текст к нижнему регистру.
    """

    tokenizer: Literal["word", "space", "prefix"] = "word"
    min_token_len: int = 2
    max_token_len: int = 20
    lowercase: bool = True

    def __post_init__(self) -> None:
        """Валидирует параметры конфигурации.

        Raises:
            ValueError: Если min/max длины токена некорректны.
        """
        if self.min_token_len < 1:
            msg = "min_token_len должен быть >= 1."
            raise ValueError(msg)

        if self.max_token_len < self.min_token_len:
            msg = "max_token_len должен быть >= min_token_len."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class QdrantKeywordIndexSpec:
    """Декларация keyword-индекса для поля payload.

    Attributes:
        field (FieldName): Имя поля payload.
    """

    field: FieldName


@dataclass(frozen=True, slots=True)
class QdrantTextIndexSpec:
    """Декларация text-индекса для поля payload.

    Attributes:
        field (FieldName): Имя поля payload.
        config (QdrantTextIndexConfig): Параметры токенизации.
    """

    field: FieldName
    config: QdrantTextIndexConfig = field(default_factory=QdrantTextIndexConfig)
