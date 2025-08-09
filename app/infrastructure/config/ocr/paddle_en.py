"""Секция настроек OCR Paddle En."""

from __future__ import annotations

from pydantic import Field

from ..base import SettingsBase


class PaddleEnOCRSettings(SettingsBase):
    """Настройки движка OCR Paddle En."""

    use_gpu: bool = Field(
        False,
        env="OCR_PADDLE_EN_USE_GPU",
        description="Включение GPU (CUDA) для Paddle En."
    )

    det: bool = Field(
        False,
        env="OCR_PADDLE_EN_DET",
        description="Включение детекции текстовых областей для Paddle En."
    )

    cls: bool = Field(
        False,
        env="OCR_PADDLE_EN_CLS",
        description="Включение классификации ориентации для Paddle En."
    )
