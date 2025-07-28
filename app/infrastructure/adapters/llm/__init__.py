"""DI-адаптеры LLM."""

from .gigachat import SberGigaChatLLMAdapter
from .null import NullLLM
from .yagpt import YaGPTLLMAdapter

__all__ = [
    "YaGPTLLMAdapter",
    "SberGigaChatLLMAdapter",
    "NullLLM",
]
