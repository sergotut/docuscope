"""Секция настроек E5 Mistral эмбеддера."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class E5MistralEmbeddingSettings(SettingsBase):
    """Настройки E5 Mistral эмбеддера."""

    host: str = Field(
        "http://localhost",
        env="EMBED_E5M_HOST",
        description="Базовый URL до llama.cpp."
    )

    port: int = Field(
        8080,
        env="EMBED_E5M_PORT",
        description="Базовый порт llama.cpp."
    )

    model_name: str = Field(
        "e5-mistral-7b-instruct",
        env="EMBED_E5M_MODEL_NAME",
        description="Модель эмбеддера E5 Mistral."
    )

    batch_size: int = Field(
        1,
        env="EMBED_E5M_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддера E5 Mistral."
    )

    dim: int = Field(
        768,
        env="EMBED_E5M_DIM",
        description="Размерность эмбеддера E5 Mistral."
    )

    max_tokens: int = Field(
        512,
        env="EMBED_E5M_MAX_TOKENS",
        description="Максимальное количество токенов эмбеддера E5 Mistra."
    )
