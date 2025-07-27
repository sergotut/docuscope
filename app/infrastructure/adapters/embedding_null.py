from app.infrastructure.protocols.embedding import EmbeddingPort


class NullEmbedder(EmbeddingPort):
    """Null-объект для эмбеддера."""

    def embed(self, texts):
        return [[0.0] * 768 for _ in texts]

    def is_healthy(self) -> bool:
        return False
