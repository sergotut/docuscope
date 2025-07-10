import structlog

logger = structlog.get_logger()

class YandexGPTEmbedding:
    def __init__(self, key: str):
        self.key = key

    def embed(self, texts: list[str]) -> list[list[float]]:
        logger.debug("embed", texts=len(texts))
        return [[0.0] * 768 for _ in texts]
