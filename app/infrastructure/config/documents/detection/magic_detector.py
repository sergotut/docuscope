"""Настройки для Magic-детектора типов документов.

Конфигурация детектора, использующего магические числа и libmagic
для определения типов документов.
"""

from __future__ import annotations

from pydantic import Field

from app.infrastructure.config.base import SettingsBase

__all__ = [
    "MagicDetectorSettings",
]


class MagicDetectorSettings(SettingsBase):
    """Настройки Magic-детектора типов документов.

    Специфичные настройки для детектора, использующего магические числа.
    Общие параметры (размер буфера, таймауты) берутся из CommonDocumentSettings.

    Attributes:
        use_libmagic: Использовать ли системную библиотеку libmagic.
        confidence_threshold: Минимальный порог уверенности для принятия решения.
        mime_conflict_penalty: Штраф за конфликт заявленного и определённого MIME.
        ooxml_confidence_cap: Максимальная уверенность для OOXML документов.
        ole_confidence_cap: Максимальная уверенность для OLE документов.
        scan_limit_multiplier: Множитель для лимита сканирования относительно head_size.
        enable_signature_cache: Включить ли кеширование сигнатур файлов.
        signature_cache_size: Размер кеша сигнатур файлов.
    """

    use_libmagic: bool = Field(
        True,
        env="DETECTOR_MAGIC_USE_LIBMAGIC",
        description="Использовать ли системную библиотеку libmagic",
    )

    confidence_threshold: float = Field(
        0.7,
        env="DETECTOR_MAGIC_CONFIDENCE_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="Минимальный порог уверенности для принятия решения",
    )

    mime_conflict_penalty: float = Field(
        0.2,
        env="DETECTOR_MAGIC_MIME_CONFLICT_PENALTY",
        ge=0.0,
        le=1.0,
        description="Штраф за конфликт заявленного и определённого MIME",
    )

    ooxml_confidence_cap: float = Field(
        0.85,
        env="DETECTOR_MAGIC_OOXML_CONFIDENCE_CAP",
        ge=0.0,
        le=1.0,
        description="Максимальная уверенность для OOXML документов",
    )

    ole_confidence_cap: float = Field(
        0.8,
        env="DETECTOR_MAGIC_OLE_CONFIDENCE_CAP",
        ge=0.0,
        le=1.0,
        description="Максимальная уверенность для OLE документов",
    )

    scan_limit_multiplier: float = Field(
        4.0,
        env="DETECTOR_MAGIC_SCAN_LIMIT_MULTIPLIER",
        ge=1.0,
        le=10.0,
        description=(
            "Множитель для лимита сканирования относительно preferred_head_size",
        ),
    )

    enable_signature_cache: bool = Field(
        True,
        env="DETECTOR_MAGIC_ENABLE_SIGNATURE_CACHE",
        description="Включить ли кеширование сигнатур файлов",
    )

    signature_cache_size: int = Field(
        1000,
        env="DETECTOR_MAGIC_SIGNATURE_CACHE_SIZE",
        ge=100,
        le=10000,
        description="Размер кеша сигнатур файлов",
    )
