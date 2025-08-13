"""Доменная модель результата OCR-распознавания.

Содержит распознанный текст и, при наличии, язык и уверенность распознавания.
"""

from dataclasses import dataclass

__all__ = ["OcrResult"]


@dataclass(frozen=True, slots=True)
class OcrResult:
    """Неизменяемая модель результата OCR.

    Attributes:
        text (str): Распознанный текст.
        language (str | None): Код языка (en | ru) или None, если язык не определён.
        confidence (float | None): Уверенность распознавания в диапазоне 0.0..1.0 или
            None, если движок её не предоставляет.
    """

    text: str
    language: str | None = None
    confidence: float | None = None
