"""Секция настроек OCR Paddle Ru."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class PaddleRuOCRSettings(SettingsBase):
    """Настройки движка OCR Paddle Ru."""

    use_gpu: bool = Field(
        False,
        env="OCR_PADDLE_RU_USE_GPU",
        description="Включение GPU (CUDA) для Paddle Ru.",
    )

    det: bool = Field(
        False,
        env="OCR_PADDLE_RU_DET",
        description="Включение детекции текстовых областей для Paddle Ru.",
    )

    cls: bool = Field(
        False,
        env="OCR_PADDLE_RU_CLS",
        description="Включение классификации ориентации для Paddle Ru.",
    )
