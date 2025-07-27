"""Маппинг ключей настроек на DI-обёртки для DI-контейнера."""

from app.infrastructure.adapters.embedding import (
    BGELargeEmbeddingAdapter,
    NullEmbedder,
    SberGigaChatEmbeddingAdapter,
    SentenceTransformersEmbeddingAdapter,
    YAGPTEmbeddingAdapter,
)
from app.infrastructure.adapters.llm import (
    NullLLM,
    SberGigaChatLLMAdapter,
    YaGPTLLMAdapter,
)
from app.infrastructure.adapters.ocr import NullOCR, PaddleOCRAdapterPort
from app.infrastructure.adapters.storage import MinIOStorageAdapter, NullStorage
from app.infrastructure.adapters.vector import NullVectorStore, QdrantVectorStoreAdapter

EMBEDDERS = {
    "yagpt": YAGPTEmbeddingAdapter,
    "gigachat": SberGigaChatEmbeddingAdapter,
    "bge_large": BGELargeEmbeddingAdapter,
    "st_all": SentenceTransformersEmbeddingAdapter,
    "null": NullEmbedder,
}
LLMS = {
    "yagpt": YaGPTLLMAdapter,
    "gigachat": SberGigaChatLLMAdapter,
    "null": NullLLM,
}
VSTORES = {
    "qdrant": QdrantVectorStoreAdapter,
    "null": NullVectorStore,
}
OCRS = {
    "paddle": PaddleOCRAdapterPort,
    "null": NullOCR,
}
STORAGES = {
    "minio": MinIOStorageAdapter,
    "null": NullStorage,
}
