"""Секция настроек Sber GigaChat эмбеддера."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class SberGigaChatEmbeddingSettings(SettingsBase):
    """Настройки Sber GigaChat эмбеддера."""

    api_key: str | None = Field(
        None,
        env="EMBED_GIGACHAT_API_KEY",
        min_length=10,
        description="API-ключ для эмбеддера Sber GigaChat.",
    )

    endpoint: str | None = Field(
        None,
        env="EMBED_GIGACHAT_ENDPOINT",
        description="Эндпоинт эмбеддера Sber GigaChat.",
    )

    model_name: str | None = Field(
        None,
        env="EMBED_GIGACHAT_MODEL_NAME",
        description="Модель эмбеддера Sber GigaChat.",
    )

    batch_size: int = Field(
        1,
        env="EMBED_GIGACHAT_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддера Sber GigaChat.",
    )

    max_tokens: int = Field(
        2048,
        env="EMBED_GIGACHAT_MAX_TOKENS",
        description="Максимальное количество токенов эмбеддера Sber GigaChat.",
    )
