"""Адаптер эмбеддера Sber GigaChat."""


class SberGigaChatEmbedding:
    """Класс для эмбеддинга через Sber GigaChat.

    Args:
        api_key (str): API-ключ GigaChat.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def embed(self, texts):
        """Получает эмбеддинги с помощью GigaChat.

        Args:
            texts (list[str]): Список текстов.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        # TODO: реализация
        pass
