"""Правило: уверенность ниже порога."""

from __future__ import annotations

from app.application.documents.detection.reasons import (
    REASON_LOW_CONFIDENCE,
    ReasonCode,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.type_detection import TypeDetectionResult

__all__ = ["ConfidenceRule"]


class ConfidenceRule:
    """Отклоняет, если уверенность ниже заданного порога."""

    def __init__(self, *, min_confidence: float) -> None:
        """Создаёт правило с порогом уверенности.

        Args:
            min_confidence (float): Минимально допустимая уверенность
                в диапазоне 0.0..1.0.

        Raises:
            ValueError: Если значение порога вне диапазона 0.0..1.0.
        """
        if not (0.0 <= min_confidence <= 1.0):
            raise ValueError("min_confidence должен быть в диапазоне 0.0..1.0")
        self._min = min_confidence

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
    ) -> ReasonCode | None:
        """Сравнивает уверенность с порогом.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (ext/mime).

        Returns:
            ReasonCode | None: Причина отклонения REASON_LOW_CONFIDENCE при
                result.confidence ниже порога, иначе None.
        """
        _ = normalized  # параметр не используется
        return REASON_LOW_CONFIDENCE if result.confidence < self._min else None
