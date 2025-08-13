"""Интерфейс (порт) для генерации ответов через LLM.

Реализуется через адаптеры GigaChat, YandexGPT и заглушки.
"""

from typing import Protocol


class LLMPort(Protocol):
    """Абстрактный порт LLM.

    Определяет интерфейс генерации текстов и проверки доступности модели.
    """

    def generate(self, prompt: str, **kwargs) -> str:
        """Генерирует ответ на основе входного промпта.

        Args:
            prompt (str): Входной текст запроса.
            **kwargs: Дополнительные параметры (например, context, temperature).

        Returns:
            str: Сгенерированный ответ модели.
        """
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность модели.

        Returns:
            bool: True, если модель доступна.
        """
        ...
