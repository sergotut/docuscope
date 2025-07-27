from app.infrastructure.protocols.llm import LLMPort

class NullLLM(LLMPort):
    def generate(self, *a, **kw):
        return "LLM недоступен"
    def is_healthy(self) -> bool:
        return False
