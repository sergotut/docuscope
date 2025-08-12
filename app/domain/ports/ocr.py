"""Порт (интерфейс) для распознавания текста (OCR)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.models.media import OcrResult
from app.domain.models.shared import Blob

__all__ = ["OCRPort"]


@runtime_checkable
class OCRPort(Protocol):
    """Абстрактный порт OCR.

    Определяет интерфейс для извлечения текста из файлов и проверки
    доступности сервиса.
    """

    async def extract_text(self, blob: Blob) -> OcrResult:
        """Распознаёт текст из бинарных данных.

        Args:
            blob (Blob): Двоичные данные файла и, при наличии, MIME-тип.

        Returns:
            OcrResult: Распознанный текст, язык и уверенность распознавания.
        """
        ...

    async def is_healthy(self) -> bool:
        """Проверяет доступность сервиса OCR.

        Returns:
            bool: True, если сервис доступен и готов к работе.
        """
        ...
