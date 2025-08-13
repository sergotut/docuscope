"""Секция базовых настроек эмбеддеров."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class EmbeddingBaseSettings(SettingsBase):
    """Базовые настройки эмбеддеров."""

    space: str = Field(
        "retrieval",
        env="EMBED_SPACE",
        description="Пространство (semantic, retrieval и др.)."
    )

    timeout: float = Field(
        30.0,
        env="EMBED_TIMEOUT",
        min_length=10,
        description="Таймаут подключения к эмбеддеру.",
    )
