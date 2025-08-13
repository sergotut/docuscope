"""Низкоуровневые адаптеры эмбеддеров.

Содержат реализацию взаимодействия с конкретными моделями эмбеддеров:
SentenceTransformers, GigaChat, YAGPT, Mistral.

Каждый адаптер реализует протокол EmbedderPort, изолируя инфраструктурную
логику от бизнес-слоя.
"""

from .e5_mistral import E5MistralEmbedder
from .gigachat import SberGigaChatEmbedder
from .sentence_transformers import SentenceTransformersEmbedder
from .yagpt import YAGPTEmbedder

__all__ = [
    "SentenceTransformersEmbedder",
    "SberGigaChatEmbedder",
    "YAGPTEmbedder",
    "E5MistralEmbedder",
]
