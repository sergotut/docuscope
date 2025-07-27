"""Адаптер эмбеддера BGE Large."""


class BGELargeEmbedding:
    """Класс для эмбеддинга через BGE Large.

    Args:
        model_name (str): Название модели.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    def embed(self, texts):
        """Получает эмбеддинги с помощью BGE Large.

        Args:
            texts (list[str]): Список текстов.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        # TODO: реализация
        pass
