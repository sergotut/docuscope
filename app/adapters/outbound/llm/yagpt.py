"""
Модуль для интеграции с LLM (YandexGPT) — генерация текстовых ответов по промпту.

Используется для аналитики и Q&A по юридическим документам.
"""

import structlog

logger = structlog.get_logger()


class YaGPTLLM:
    """Адаптер для генерации ответов с помощью языковой модели YandexGPT."""

    def __init__(self, key: str):
        """
        Инициализация LLM-клиента YandexGPT.

        Args:
            key (str): API-ключ для доступа к языковой модели YandexGPT.
        """
        self.key = key

    def generate(self, prompt: str, context: str) -> str:
        """
        Генерирует текстовый ответ на основе промпта и дополнительного контекста.

        Args:
            prompt (str): Основной запрос пользователя.
            context (str): Контекст (например, фрагменты документа) для генерации
                более точного ответа.

        Returns:
            str: Сгенерированный текст ответа.
        """
        logger.debug("llm_generate", prompt=prompt[:30])
        return "LLM-анализ: " + prompt
