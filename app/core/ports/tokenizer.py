"""Порт токенайзера."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TokenizerPort(Protocol):
    """Абстрактный порт токенайзера."""

    def count_tokens(self, text: str) -> int:
        """Возвращает количество токенов в строке.

        Args:
            text (str): Входной текст.

        Returns:
            int: Количество токенов.
        """
        ...

    def is_healthy(self) -> bool:
        """Короткий bool-check, основанный на методе health.

        Returns:
            bool: True, если токенайзер доступен.
        """
        ...

    def health(self) -> dict[str, Any]:
        """Расширенный health-report.

        Возвращает словарь с метаинформацией, например:
        - model: str
        - vocab_size: int
        - encoding: str
        - version: str

        Returns:
            dict[str, Any]: Состояние токенайзера.
        """
        ...
