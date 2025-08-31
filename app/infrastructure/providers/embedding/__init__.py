"""DI-адаптеры эмбеддеров."""

from ..fallback.embedding import FallbackEmbeddingAdapter
from .bge_large import BGELargeEmbeddingAdapter
from .bge_large_ru import BGELargeRuEmbeddingAdapter
from .e5_mistral import E5MistralEmbeddingAdapter
from .gigachat import SberGigaChatEmbeddingAdapter
from .null import NullEmbedder
from .sbert_large_ru import SBERTLargeRuEmbeddingAdapter
from .sentence_transformers import SentenceTransformersEmbeddingAdapter
from .yagpt import YAGPTEmbeddingAdapter

__all__ = [
    "YAGPTEmbeddingAdapter",
    "SberGigaChatEmbeddingAdapter",
    "BGELargeEmbeddingAdapter",
    "BGELargeRuEmbeddingAdapter",
    "SBERTLargeRuEmbeddingAdapter",
    "E5MistralEmbeddingAdapter",
    "SentenceTransformersEmbeddingAdapter",
    "FallbackEmbeddingAdapter",
    "NullEmbedder",
]
