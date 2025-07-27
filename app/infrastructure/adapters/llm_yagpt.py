from app.adapters.outbound.llm_yagpt import YaGPTLLM
from app.core.settings import settings
from app.infrastructure.protocols.llm import LLMPort


class YaGPTLLMAdapter(YaGPTLLM, LLMPort):
    def __init__(self) -> None:
        super().__init__(key=settings.ygpt_key)

    def is_healthy(self) -> bool:
        return True
