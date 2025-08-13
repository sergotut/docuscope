"""Протоколы для типизации tiktoken-энкодера.

Минимальный интерфейс, чтобы не зависеть жёстко от SDK.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["EncoderLike"]


@runtime_checkable
class EncoderLike(Protocol):
    """Минимальный интерфейс энкодера tiktoken.

    Attributes:
        n_vocab (int): Размер словаря.
    """

    @property
    def n_vocab(self) -> int:
        """Размер словаря.

        Returns:
            int: Количество токенов в словаре.
        """
        ...

    def encode(self, text: str) -> list[int]:
        """Кодирует текст в список токенов.

        Args:
            text (str): Входной текст.

        Returns:
            list[int]: Идентификаторы токенов.
        """
        ...
