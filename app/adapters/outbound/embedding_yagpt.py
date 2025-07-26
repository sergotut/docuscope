"""
Модуль для работы с эмбеддингами через YandexGPT.

Реализует адаптер для получения векторных представлений текста.
"""

import structlog

logger = structlog.get_logger()


class YandexGPTEmbedding
    """
    Адаптер для генерации эмбеддингов текстов с помощью YandexGPT Embeddings API.
    """
    
    def __init__(self, key: str):
        """
        Инициализация адаптера эмбеддингов YandexGPT.

        Args:
            key (str): API-ключ для доступа к сервису YandexGPT.
        """
        self.key = key

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Получает эмбеддинги для списка текстов.

        Args:
            texts (list[str]): Список строк для преобразования в эмбеддинги.

        Returns:
            list[list[float]]: Список эмбеддингов (каждый эмбеддинг — список float).
        """
        logger.debug("embed", texts=len(texts))
        return [[0.0] * 768 for _ in texts]
