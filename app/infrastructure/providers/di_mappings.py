"""Маппинг ключей настроек на DI-обёртки для DI-контейнера."""

from .embedding import (
    YAGPTEmbeddingAdapter,
    SberGigaChatEmbeddingAdapter,
    SBERTLargeRuEmbeddingAdapter,
    E5MistralEmbeddingAdapter,
    BGELargeEmbeddingAdapter,
    BGELargeRuEmbeddingAdapter,
    SentenceTransformersEmbeddingAdapter,
    NullEmbedder,
)
from .storage import MinioStorageAdapter

EMBEDDERS = {
    "yagpt": YAGPTEmbeddingAdapter,
    "gigachat": SberGigaChatEmbeddingAdapter,
    "sbert_large_ru": SBERTLargeRuEmbeddingAdapter,
    "e5_mistral": E5MistralEmbeddingAdapter,
    "bge_large": BGELargeEmbeddingAdapter,
    "bge_large_ru": BGELargeRuEmbeddingAdapter,
    "st_all": SentenceTransformersEmbeddingAdapter,
    "null": NullEmbedder,
}

STORAGE = {
    "minio": MinioStorageAdapter,
}
