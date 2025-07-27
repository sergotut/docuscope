from app.adapters.outbound.vectordb_qdrant import QdrantVectorStore
from app.core.settings import settings
from app.infrastructure.protocols.vector import VectorStorePort

class QdrantVectorStoreAdapter(QdrantVectorStore, VectorStorePort):
    def __init__(self) -> None:
        super().__init__(url=getattr(settings, "qdrant_url", "http://localhost:6333"))
    def is_healthy(self) -> bool:
        return True
