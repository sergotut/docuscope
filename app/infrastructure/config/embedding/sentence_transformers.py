"""Секция настроек моделей эмбеддеров Sentence-Transformers."""

from __future__ import annotations

from pydantic import Field

from typing import Literal, Optional

from pydantic import Field, validator

from ..base import SettingsBase


class STEmbeddingSettings(SettingsBase):
    """Настройки эмбеддеров Sentence-Transformers."""

    model_name: Optional[str|None] = Field(
        None,
        env="EMBED_ST_MODEL_NAME",
        description="Модель эмбеддеров Sentence-Transformers."
    )
    
    device: Optional[str|None] = Field(
        None,
        env="EMBED_ST_DEVICE",
        description="Устройство инференса (cpu/cuda)."
    )

    dtype: Literal["float32", "float16", "bfloat16"] = Field(
        "float32",
        env="EMBED_ST_DTYPE",
        description="Тип тензора ('float32', 'float16', 'bfloat16')."
    )

    quantized: bool = Field(
        False,
        env="EMBED_ST_QUANTIZED",
        description="Загрузка модели в 8-битном режиме."
    )

    batch_size: int = Field(
        1,
        env="EMBED_ST_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддеров Sentence-Transformers."
    )

    max_tokens: int = Field(
        512,
        env="EMBED_ST_MAX_TOKENS",
        description="Максимальное количество токенов модели."
    )
