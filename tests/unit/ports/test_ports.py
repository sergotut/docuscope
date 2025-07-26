""" Базовые unit-тесты для проверки структуры портов. """

from app.ports import (
    EmbeddingPort,
    OCRPort,
    VectorStorePort,
    LLMPort,
    StoragePort,
)


def test_ports_are_abc() -> None:
    """Проверяет, что все порты наследуются от ABC."""
    assert EmbeddingPort.__mro__[-2].__name__ == "ABC"
    assert OCRPort.__mro__[-2].__name__ == "ABC"
    assert VectorStorePort.__mro__[-2].__name__ == "ABC"
    assert LLMPort.__mro__[-2].__name__ == "ABC"
    assert StoragePort.__mro__[-2].__name__ == "ABC"
