from qdrant_client import QdrantClient
import structlog

logger = structlog.get_logger()

class QdrantVectorStore:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)
        self.collection = "documents"
        logger.info("qdrant_client_ready", url=url, collection=self.collection)

    def upsert(self, vectors, payloads):
        self.client.upsert(
            collection_name=self.collection,
            points=vectors,
            payloads=payloads,
        )
        logger.debug("qdrant_upsert", vectors=len(vectors))
