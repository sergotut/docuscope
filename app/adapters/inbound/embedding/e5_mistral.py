"""DI-адаптер E5-Mistral.

Подключает локальный REST-эндпоинт llama.cpp, реализующий модель E5-Mistral.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound.embedding.e5_mistral import E5MistralEmbedding
from app.core.settings import settings

logger = structlog.get_logger(__name__)


class E5MistralEmbeddingAdapter(E5MistralEmbedding):
    """Использует локальный llama.cpp-эндпоинт."""

    def __init__(self) -> None:
        """Создаёт адаптер с параметрами из ENV.

        Используются переменные:
            - settings.ai.e5_mistral_host
            - settings.ai.e5_mistral_model
        """
        super().__init__(
            host=settings.ai.e5_mistral_host,
            model_name=settings.ai.e5_mistral_model,
        )
        logger.info(
            "Создан E5MistralEmbeddingAdapter",
            host=settings.ai.e5_mistral_host,
            model=settings.ai.e5_mistral_model,
        )
