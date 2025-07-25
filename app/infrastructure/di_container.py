import structlog
from dependency_injector import containers, providers

from app.adapters.outbound.embedding_yagpt import YandexGPTEmbedding
from app.adapters.outbound.llm_yagpt import YaGPTLLM
from app.adapters.outbound.ocr_paddle import PaddleOCRAdapter
from app.adapters.outbound.storage_minio import MinIOStorage
from app.adapters.outbound.vectordb_qdrant import QdrantVectorStore
from app.core.settings import settings

logger = structlog.get_logger()


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    logger = providers.Singleton(lambda: logger)

    embedding = providers.Singleton(YandexGPTEmbedding, key=settings.ygpt_key)
    vectordb = providers.Singleton(QdrantVectorStore, url=settings.vector_backend)
    storage = providers.Singleton(
        MinIOStorage,
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
    )
    ocr = providers.Singleton(PaddleOCRAdapter)
    llm = providers.Singleton(YaGPTLLM, key=settings.ygpt_key)


container = Container()
