class YandexGPTEmbedding:
    def __init__(self, key: str):
        self.key = key
    def embed(self, texts: list[str]) -> list[list[float]]:
        # Мок: возвращаем список "нулевых" векторов
        return [[0.0]*768 for _ in texts]
