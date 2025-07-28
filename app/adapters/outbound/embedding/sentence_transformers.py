"""Адаптер эмбеддера Sentence Transformers."""


class SentenceTransformersEmbedding:
    """Класс для эмбеддинга через Sentence Transformers.

    Args:
        model_name (str): Название модели.
    """

    def __init__(self, model_name: str):
        """Инициализация адаптера эмбеддингов.

        Args:
            model_name (str): Имя модели эмбеддинга.
        """
        self.model_name = model_name

    def embed(self, texts):
        """Получает эмбеддинги с помощью Sentence Transformers.

        Args:
            texts (list[str]): Список текстов.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        # TODO: реализация
        pass
