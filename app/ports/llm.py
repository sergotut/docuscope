""" Порт для LLM-провайдеров. """

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMPort(ABC):
    """
    Абстракция генеративной модели.

    Methods:
        generate: Генерирует ответ на заданный prompt.
    """

    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.2) -> str:
        """
        Генерирует ответ на указанный prompt.

        Args:
            prompt (str): Текст запроса к модели.
            temperature (float, optional): Температура выборки. По умолчанию 0.2.

        Returns:
            str: Сгенерированный ответ модели.
        """
        raise NotImplementedError
