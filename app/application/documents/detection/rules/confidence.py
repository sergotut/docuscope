"""Правило: уверенность ниже порога."""

from __future__ import annotations

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_LOW_CONFIDENCE
)
from app.application.documents.detection.rules.base import DecisionRule
from app.application.documents import (
    NormalizedInput,
    TypeDetectionResult
)

__all__ = ["ConfidenceRule"]


class ConfidenceRule:
    """Отклоняет, если уверенность ниже заданного порога."""

    def __init__(self, *, min_confidence: float) -> None:
        if not (0.0 <= min_confidence <= 1.0):
            raise ValueError("min_confidence должен быть в диапазоне 0.0..1.0")
        self._min = min_confidence

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
        warnings: tuple[WarningCode, ...],
    ) -> ReasonCode | None:
        """Сравнивает уверенность с порогом.

        Args:
            result: Доменный результат детекции типа.
            normalized: Нормализованные входные данные (ext/mime).
            warnings: Предупреждения нормализации и/или детектора.

        Returns:
            Причину отклонения REASON_LOW_CONFIDENCE при result.confidence
            ниже порога; иначе None.
        """
        return REASON_LOW_CONFIDENCE if result.confidence < self._min else None
