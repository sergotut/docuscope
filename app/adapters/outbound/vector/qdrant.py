"""Адаптер для Qdrant Vector Store."""


class QdrantVectorStore:
    """Класс для работы с Qdrant.

    Args:
        url (str): URL Qdrant.
    """

    def __init__(self, url: str):
        """Создаёт подключение к Qdrant.

        Args:
            url (str): url путь до сервиса Qdrant.
        """
        self.url = url

    def upsert(self, vectors, payloads):
        """Загружает векторы в Qdrant.

        Args:
            vectors (list[list[float]]): Векторы.
            payloads (list[dict]): Метаданные.
        """
        # TODO: реализация
        pass

    def hybrid_search(self, query: str, top_k: int):
        """Выполняет гибридный поиск по Qdrant.

        Args:
            query (str): Поисковый запрос.
            top_k (int): Кол-во результатов.

        Returns:
            list[dict]: Список найденных объектов.
        """
        # TODO: реализация
        pass
