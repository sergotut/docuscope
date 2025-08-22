"""Правило: неизвестное расширение."""

from __future__ import annotations

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_UNKNOWN_EXTENSION
)
from app.application.documents.detection.rules.base import DecisionRule
from app.application.documents import NormalizedInput, TypeDetectionResult

__all__ = ["UnknownExtensionRule"]


class UnknownExtensionRule:
    """Отклоняет, если нормализация не смогла определить расширение."""

    def __init__(self, *, enabled: bool = False) -> None:
        self._enabled = enabled

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
        warnings: tuple[WarningCode, ...],
    ) -> ReasonCode | None:
        """Проверяет факт отсутствия или некорректности расширения.

        Args:
            result: Доменный результат детекции типа.
            normalized: Нормализованные входные данные (ext/mime).
            warnings: Предупреждения нормализации и/или детектора.

        Returns:
            Причину отклонения REASON_UNKNOWN_EXTENSION, если расширение
            отсутствует или не было канонизировано; иначе None.
        """
        if not self._enabled:
            return None
        return REASON_UNKNOWN_EXTENSION if normalized.ext is None else None
