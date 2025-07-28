"""DI-адаптеры эмбеддеров."""

from .bge_large import BGELargeEmbeddingAdapter
from .gigachat import SberGigaChatEmbeddingAdapter
from .null import NullEmbedder
from .sentence_transformers import SentenceTransformersEmbeddingAdapter
from .yagpt import YAGPTEmbeddingAdapter

__all__ = [
    "YAGPTEmbeddingAdapter",
    "SberGigaChatEmbeddingAdapter",
    "BGELargeEmbeddingAdapter",
    "SentenceTransformersEmbeddingAdapter",
    "NullEmbedder",
]
