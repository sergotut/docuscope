"""
DI-адаптеры LLM.
"""

from .yagpt import YaGPTLLMAdapter
from .gigachat import SberGigaChatLLMAdapter
from .null import NullLLM

__all__ = [
    "YaGPTLLMAdapter",
    "SberGigaChatLLMAdapter",
    "NullLLM",
]
