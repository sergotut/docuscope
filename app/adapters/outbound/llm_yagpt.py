class YaGPTLLM:
    def __init__(self, key: str):
        self.key = key
    def generate(self, prompt: str, context: str) -> str:
        return "LLM-анализ: " + prompt
