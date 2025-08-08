"""Секция настроек эмбеддера SBERT Large RU (Sentence-Transformers)."""

from __future__ import annotations

from typing import Literal
import torch

from pydantic import Field, validator

from ..base import SettingsBase


class SBERTLargeRuEmbeddingSettings(SettingsBase):
    """Настройки эмбеддера SBERT Large RU."""

    model_name: str = Field(
        ...,
        env="EMBED_SBERT_LARGE_RU_MODEL_NAME",
        description="Модель эмбеддера SBERT Large RU."
    )
    
    device: Optional[str] = Field(
        default=None,
        env="EMBED_SBERT_LARGE_RU_DEVICE",
        description="Устройство инференса (cpu/cuda) … "
                    "(если None — определяется автоматически).",
    )

    dtype: Literal["float32", "float16", "bfloat16"] = Field(
        "float32",
        env="EMBED_SBERT_LARGE_RU_DTYPE",
        description="Тип тензоров при загрузке модели."
    )

    quantized: bool = Field(
        False,
        env="EMBED_SBERT_LARGE_RU_QUANTIZED",
        description="Загрузка модели в 8-битном режиме."
    )

    batch_size: int = Field(
        1,
        env="EMBED_SBERT_LARGE_RU_BATCH_SIZE",
        ge=1,
        description="Размер батча эмбеддеров SBERT Large RU."
    )

    max_tokens: int = Field(
        512,
        env="EMBED_SBERT_LARGE_RU_MAX_TOKENS",
        description="Максимальное количество токенов модели."
    )

    @validator("device", pre=True, always=True)
    def _auto_device(cls, v: str | None) -> str:
        """Автоопределение устройства инференса (cpu/cuda)

        Args:
            v (str): Значение из конфига.
        Returns:
            str: Устройство инференса (cpu/cuda).
        """
        return v or ("cuda" if torch.cuda.is_available() else "cpu")
