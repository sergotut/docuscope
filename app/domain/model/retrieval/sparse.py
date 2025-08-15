"""Доменные модели для разрежённого вектора .

(TF-IDF/BM25/SPLADE-подобный).
Определяет неизменяемую структуру данных со списками индексов и значений,
а также базовую валидацию согласованности.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import VectorStoreError

__all__ = ["SparseVector"]


@dataclass(slots=True, frozen=True)
class SparseVector:
    """Разрежённый вектор.

    Attributes:
        indices (list[int]): Индексы ненулевых координат.
        values (list[float]): Значения весов по соответствующим индексам.
    """

    indices: list[int]
    values: list[float]

    def __post_init__(self) -> None:
        """Проверяет согласованность индексов и значений.

        Raises:
            VectorStoreError: Если длины не совпадают или индексы некорректны.
        """
        if len(self.indices) != len(self.values):
            msg = "Длины indices и values должны совпадать."
            raise VectorStoreError(msg)
        if any(i < 0 for i in self.indices):
            msg = "Все indices должны быть неотрицательными."
            raise VectorStoreError(msg)
