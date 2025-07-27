from typing import Protocol


class LLMPort(Protocol):
    """Абстрактный порт LLM."""

    def generate(self, prompt: str, **kwargs) -> str: ...
    def is_healthy(self) -> bool: ...
