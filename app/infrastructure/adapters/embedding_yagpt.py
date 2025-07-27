from app.adapters.outbound.embedding_yagpt import YandexGPTEmbedding
from app.core.settings import settings
from app.infrastructure.protocols.embedding import EmbeddingPort

class YAGPTEmbeddingAdapter(YandexGPTEmbedding, EmbeddingPort):
    """Эмбеддер Яндекс GPT."""
    def __init__(self) -> None:
        super().__init__(key=settings.ygpt_key)
    def is_healthy(self) -> bool:
        return True
