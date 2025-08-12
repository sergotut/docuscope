"""Порт токенайзера.

Возвращает доменную модель TokenCount и типизированный health-report.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.diagnostics import TokenizerHealthReport
from app.domain.model.shared import TokenCount

__all__ = ["TokenizerPort"]


@runtime_checkable
class TokenizerPort(Protocol):
    """Абстрактный порт токенайзера."""

    def count_tokens(self, text: str) -> TokenCount:
        """Возвращает количество токенов в строке.

        Args:
            text (str): Входной текст.

        Returns:
            TokenCount: Количество токенов.
        """
        ...

    def is_healthy(self) -> bool:
        """Короткий bool-check, основанный на методе health.

        Returns:
            bool: True, если токенайзер доступен.
        """
        ...

    def health(self) -> TokenizerHealthReport:
        """Расширенный health-report.

        Returns:
            TokenizerHealthReport: Метаинформация о состоянии токенайзера.
        """
        ...
