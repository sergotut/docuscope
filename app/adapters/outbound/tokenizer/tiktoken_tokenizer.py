"""Токенизатор на базе tiktoken.

Берет модель из TokenizerSettings, либо переопределяет из переменной.
Реализует TokenizerPort.
"""

from __future__ import annotations

import tiktoken

from typing import Any

from app.core.ports.tokenizer import TokenizerPort
from app.core.settings.tokenizer import TokenizerSettings

_SETTINGS = TokenizerSettings()  # читает TOKENIZER_MODEL из .env


class TiktokenTokenizer(TokenizerPort):
    """Адаптер токенайзера.

    Модель берётся из TokenizerSettings (переменная TOKENIZER_MODEL),
    либо переопределяется аргументом model_name.
    """

    def __init__(self, model_name: str | None = None) -> None:
        """Инициализирует токенайзер с заданной моделью.

        Args:
            model_name (str | None): Название модели.
        """
        self._model_name: str = model_name
        self._enc = tiktoken.get_encoding(self._model_name)

    def count_tokens(self, text: str) -> int:
        """Подсчитывает количество токенов в строке.

        Args:
            text (str): Входной текст.

        Returns:
            int: Количество токенов.
        """
        return len(self._enc.encode(text))

    def is_healthy(self) -> bool:
        """Быстрый bool-check на основе метода health.

        Returns:
            bool: True, если статус токенизатора "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, Any]:
        """Возвращает расширенный отчёт о состоянии токенизатора.

        Returns:
            dict[str, str | int | float | bool | None]: Поле статус,
                модель, размерность.
        """
        try:
            vocab_size = self._enc.n_vocab
            return {
                "status": "ok",
                "model": self._model_name,
                "vocab_size": vocab_size,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "model": self._model_name,
                "error": str(exc),
            }
