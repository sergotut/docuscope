"""
Пакет с абстрактными протоколами (портами) инфраструктурного слоя.

Содержит абстракции для эмбеддинга, LLM, OCR, хранилища и векторной базы.
Все протоколы доступны для импорта напрямую из app.infrastructure.protocols.
"""

from .embedding import EmbeddingPort
from .llm import LLMPort
from .ocr import OCRPort
from .storage import StoragePort
from .vector_store import VectorStorePort

__all__ = [
    "EmbeddingPort",
    "LLMPort",
    "OCRPort",
    "StoragePort",
    "VectorStorePort",
]
