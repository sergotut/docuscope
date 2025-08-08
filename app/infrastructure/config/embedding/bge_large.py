"""Секция настроек эмбеддера BGE Large (Sentence-Transformers)."""

from __future__ import annotations

from typing import Literal
import torch

from pydantic import Field, Optional, validator

from ..base import SettingsBase


class BGELargeEmbeddingSettings(SettingsBase):
    """Настройки эмбеддера BGE Large."""

    model_name: str = Field(
        "BAAI/bge-large-en",
        env="EMBED_BGE_LARGE_MODEL_NAME",
        description="Модель эмбеддера BGE Large."
    )
    
    device: Optional[str | None] = Field(
        None,
        env="EMBED_BGE_LARGE_DEVICE",
        description="Устройство инференса (cpu/cuda) … "
                    "(если None — определяется автоматически).",
    )

    dtype: Literal["float32", "float16", "bfloat16"] = Field(
        "float32",
        env="EMBED_BGE_LARGE_DTYPE",
        description="Тип тензоров при загрузке модели."
    )

    quantized: bool = Field(
        False,
        env="EMBED_BGE_LARGE_QUANTIZED",
        description="Загрузка модели в 8-битном режиме."
    )

    batch_size: int = Field(
        1,
        env="EMBED_BGE_LARGE_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддеров BGE Large."
    )

    max_tokens: int = Field(
        512,
        env="EMBED_BGE_LARGE_MAX_TOKENS",
        description="Максимальное количество токенов модели."
    )

    @validator("device", pre=True, always=True)
    def _auto_device(cls, v: str | None) -> str:
        """Автоопределение устройства инференса (cpu/cuda).

        Args:
            v (str): Значение из конфига.
        Returns:
            str: Устройство инференса (cpu/cuda).
        """
        return v or ("cuda" if torch.cuda.is_available() else "cpu")
