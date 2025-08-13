"""Доменные модели эмбеддингов.

Содержит неизменяемые структуры для одного вектора и батча векторов.
"""

from dataclasses import dataclass

__all__ = ["EmbeddingVector", "EmbeddingBatch"]


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """Неизменяемый эмбеддинг (вектор чисел с плавающей точкой).

    Attributes:
        values (tuple[float, ...]): Координаты вектора.
    """

    values: tuple[float, ...]

    @property
    def dim(self) -> int:
        """Возвращает размерность вектора."""
        return len(self.values)


@dataclass(frozen=True, slots=True)
class EmbeddingBatch:
    """Неизменяемая коллекция эмбеддингов одинаковой размерности.

    Attributes:
        vectors (tuple[EmbeddingVector, ...]): Кортеж эмбеддингов.
    """

    vectors: tuple[EmbeddingVector, ...]

    def __len__(self) -> int:
        """Возвращает количество векторов в батче."""
        return len(self.vectors)

    @property
    def dim(self) -> int:
        """Возвращает общую размерность векторов в батче.

        Если батч пустой, возвращает 0.
        """
        return self.vectors[0].dim if self.vectors else 0
