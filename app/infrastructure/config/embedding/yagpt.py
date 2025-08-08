"""Секция настроек YaGPT эмбеддера."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class YaGPTEmbeddingSettings(SettingsBase):
    """Настройки YaGPT эмбеддера."""

    api_key: str | None = Field(
        None,
        env="EMBED_YAGPT_API_KEY",
        min_length=10,
        description="API-ключ для эмбеддера YaGPT.",
    )

    endpoint: str | None = Field(
        None,
        env="EMBED_YAGPT_ENDPOINT",
        description="Эндпоинт эмбеддера YaGPT."
    )

    model_name: str | None = Field(
        None,
        env="EMBED_YAGPT_MODEL_NAME",
        description="Модель эмбеддера YaGPT."
    )

    folder_id: str | None = Field(
        None,
        env="EMBED_YAGPT_FOLDER_ID",
        description="Идентификатор каталога в Yandex Cloud."
    )

    batch_size: int = Field(
        1,
        env="EMBED_YAGPT_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддера YaGPT."
    )
