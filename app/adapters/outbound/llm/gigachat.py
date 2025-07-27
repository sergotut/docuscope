"""Адаптер LLM Sber GigaChat."""


class SberGigaChatLLM:
    """Класс для LLM через Sber GigaChat.

    Args:
        api_key (str): API-ключ GigaChat.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, prompt: str):
        """Генерирует ответ с помощью GigaChat.

        Args:
            prompt (str): Входной текст.

        Returns:
            str: Ответ модели.
        """
        # TODO: реализация
        pass
