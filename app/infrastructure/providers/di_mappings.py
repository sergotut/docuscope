"""Маппинг ключей настроек на DI-обёртки для DI-контейнера."""

from .documents.di_mappings import (
    DOCUMENT_CONVERTERS,
    DOCUMENT_INPUT_VALIDATORS,
    DOCUMENT_TYPE_DETECTORS,
)
from .embedding import (
    BGELargeEmbeddingAdapter,
    BGELargeRuEmbeddingAdapter,
    E5MistralEmbeddingAdapter,
    NullEmbedder,
    SberGigaChatEmbeddingAdapter,
    SBERTLargeRuEmbeddingAdapter,
    SentenceTransformersEmbeddingAdapter,
    YAGPTEmbeddingAdapter,
)
from .ocr import (
    PaddleEnOCRAdapter,
    PaddleRuOCRAdapter,
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

OCR = {
    "paddle_ru": PaddleRuOCRAdapter,
    "paddle_en": PaddleEnOCRAdapter,
}

# Новые маппинги для документов
DOCUMENT_TYPE_DETECTORS = DOCUMENT_TYPE_DETECTORS
DOCUMENT_CONVERTERS = DOCUMENT_CONVERTERS
DOCUMENT_INPUT_VALIDATORS = DOCUMENT_INPUT_VALIDATORS
