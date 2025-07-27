"""
Маппинг ключей настроек на DI-обёртки для DI-контейнера.
"""

from app.infrastructure.adapters.embedding import (
    YAGPTEmbeddingAdapter,
    SberGigaChatEmbeddingAdapter,
    BGELargeEmbeddingAdapter,
    SentenceTransformersEmbeddingAdapter,
    NullEmbedder,
)
from app.infrastructure.adapters.llm import (
    YaGPTLLMAdapter,
    SberGigaChatLLMAdapter,
    NullLLM,
)
from app.infrastructure.adapters.vector import QdrantVectorStoreAdapter, NullVectorStore
from app.infrastructure.adapters.ocr import PaddleOCRAdapterPort, NullOCR
from app.infrastructure.adapters.storage import MinIOStorageAdapter, NullStorage

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
