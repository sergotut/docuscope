from qdrant_client import QdrantClient

class QdrantVectorStore:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)
        self.collection = "documents"

    def upsert(self, vectors, payloads):
        self.client.upsert(
            collection_name=self.collection,
            points=vectors,
            payloads=payloads,
        )
