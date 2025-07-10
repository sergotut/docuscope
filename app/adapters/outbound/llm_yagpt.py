import structlog

logger = structlog.get_logger()

class YaGPTLLM:
    def __init__(self, key: str):
        self.key = key

    def generate(self, prompt: str, context: str) -> str:
        logger.debug("llm_generate", prompt=prompt[:30])
        return "LLM-анализ: " + prompt
