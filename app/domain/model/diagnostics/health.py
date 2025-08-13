"""Модели health-чеков и техинфы сервисов."""

from typing import TypedDict

__all__ = [
    "TokenizerHealthReport",
    "EmbedderHealthReport",
    "LLMHealthReport",
    "VectorStoreHealthReport",
]


class TokenizerHealthReport(TypedDict, total=False):
    """Расширенный отчёт токенайзера.

    Attributes:
        model (str): Имя/идентификатор модели.
        vocab_size (int): Размер словаря.
        encoding (str): Название кодировки/правил токенизации.
        version (str): Версия движка.
    """

    model: str
    vocab_size: int
    encoding: str
    version: str


class EmbedderHealthReport(TypedDict, total=False):
    """Расширенный отчёт эмбеддера.

    Attributes:
        model (str): Имя/идентификатор модели эмбеддингов.
        dim (int): Размерность эмбеддинга.
        framework (str): Фреймворк исполнения (например, torch).
        device (str): Устройство исполнения (cpu, cuda, mps).
        version (str): Версия движка/библиотеки.
    """

    model: str
    dim: int
    framework: str
    device: str
    version: str


class LLMHealthReport(TypedDict, total=False):
    """Расширенный отчёт LLM.

    Attributes:
        model (str): Имя/идентификатор LLM.
        provider (str): Провайдер/хостинг (например, openai, local).
        context_window (int): Максимальный контекст в токенах.
        max_output_tokens (int): Лимит вывода в токенах.
        version (str): Версия API/модели.
    """

    model: str
    provider: str
    context_window: int
    max_output_tokens: int
    version: str


class VectorStoreHealthReport(TypedDict, total=False):
    """Расширенный отчёт векторного хранилища (например, Qdrant).

    Attributes:
        engine (str): Название движка.
        version (str): Версия сервиса.
        distance (str): Метрика расстояния (cosine, dot, euclid).
        collections (int): Количество коллекций.
        status (str): Текущий статус/режим работы.
    """

    engine: str
    version: str
    distance: str
    collections: int
    status: str
