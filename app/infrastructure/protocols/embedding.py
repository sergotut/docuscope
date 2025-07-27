from typing import List, Protocol


class EmbeddingPort(Protocol):
    """Абстрактный порт эмбеддера."""

    def embed(self, texts: list[str]) -> List[list[float]]: ...
    def is_healthy(self) -> bool: ...
