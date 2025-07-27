"""
Секция настроек искусственного интеллекта (AI).
"""

from .base import SettingsBase
from pydantic import Field

class AISettings(SettingsBase):
    """Настройки AI/LLM/Embedding."""

    embedder: str = Field("yagpt", description="Модель эмбеддинга")
    llm_provider: str = Field("yagpt", description="Провайдер LLM")
    vector_backend: str = Field("qdrant", description="Бэкенд векторного поиска")
    bge_large_model: str = Field("BAAI/bge-large-en-v1", description="Имя BGE Large")
    st_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="Имя модели Sentence Transformers")
    ygpt_key: str = Field("", description="API-ключ YandexGPT")
    gigachat_key: str = Field("", description="API-ключ Sber GigaChat")
