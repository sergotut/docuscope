"""Низкоуровневые адаптеры эмбеддеров.

Содержат реализацию взаимодействия с конкретными моделями эмбеддинга:
SentenceTransformers, GigaChat, YAGPT, Mistral.

Каждый адаптер реализует протокол EmbeddingPort, изолируя инфраструктурную
логику от бизнес-слоя.
"""

from .e5_mistral import E5MistralEmbedding
from .gigachat import SberGigaChatEmbedding
from .sentence_transformers import SentenceTransformersEmbedding
from .yagpt import YAGPTEmbedding

__all__ = [
    "SentenceTransformersEmbedding",
    "SberGigaChatEmbedding",
    "YAGPTEmbedding",
    "E5MistralEmbedding",
]
