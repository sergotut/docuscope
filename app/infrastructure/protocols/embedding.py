from typing import Protocol, List

class EmbeddingPort(Protocol):
    """Абстрактный порт эмбеддера."""
    def embed(self, texts: list[str]) -> List[list[float]]:
        ...
    def is_healthy(self) -> bool:
        ...
