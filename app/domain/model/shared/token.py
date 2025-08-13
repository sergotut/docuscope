"""Доменная модель счётчика токенов.

Представляет неизменяемое количество токенов.
"""

from dataclasses import dataclass

from app.domain.exceptions import TokenError

__all__ = ["TokenCount"]


@dataclass(frozen=True, slots=True)
class TokenCount:
    """Неизменяемое количество токенов.

    Attributes:
        count (int): Целое неотрицательное число токенов.
    """

    count: int

    def __post_init__(self) -> None:
        """Проверяет валидность значения.

        Raises:
            TokenError: Если значение count отрицательное.
        """
        if self.count < 0:
            msg = f"count должен быть неотрицательным, получено: {self.count}"
            raise TokenError(msg)
