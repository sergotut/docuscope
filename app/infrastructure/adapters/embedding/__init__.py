"""
DI-адаптеры эмбеддеров.
"""

from .yagpt import YAGPTEmbeddingAdapter
from .gigachat import SberGigaChatEmbeddingAdapter
from .bge_large import BGELargeEmbeddingAdapter
from .sentence_transformers import SentenceTransformersEmbeddingAdapter
from .null import NullEmbedder

__all__ = [
    "YAGPTEmbeddingAdapter",
    "SberGigaChatEmbeddingAdapter",
    "BGELargeEmbeddingAdapter",
    "SentenceTransformersEmbeddingAdapter",
    "NullEmbedder",
]
