"""Секция настроек Sber GigaChat эмбеддера."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from ..base import SettingsBase


class SberGigaChatEmbeddingSettings(SettingsBase):
    """Настройки Sber GigaChat эмбеддера."""

    api_key: Optional[str|None] = Field(
        None,
        env="EMBED_GIGACHAT_API_KEY",
        min_length=10,
        description="API-ключ для эмбеддера Sber GigaChat.",
    )

    endpoint: Optional[str|None] = Field(
        None,
        env="EMBED_GIGACHAT_ENDPOINT",
        description="Эндпоинт эмбеддера Sber GigaChat."
    )

    model_name: Optional[str|None] = Field(
        None,
        env="EMBED_GIGACHAT_MODEL_NAME",
        description="Модель эмбеддера Sber GigaChat."
    )

    batch_size: int = Field(
        1,
        env="EMBED_GIGACHAT_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддера Sber GigaChat."
    )
