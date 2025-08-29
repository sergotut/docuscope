"""Правило: неизвестное расширение."""

from __future__ import annotations

from app.application.documents.detection.reasons import (
    REASON_UNKNOWN_EXTENSION,
    ReasonCode,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.type_detection import TypeDetectionResult

__all__ = ["UnknownExtensionRule"]


class UnknownExtensionRule:
    """Отклоняет, если нормализация не смогла определить расширение."""

    def __init__(self, *, enabled: bool = False) -> None:
        """Создаёт правило.

        Args:
            enabled (bool): Включает или отключает проверку правила.
        """
        self._enabled = enabled

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
    ) -> ReasonCode | None:
        """Проверяет факт отсутствия или некорректности расширения.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничное расширение и MIME).

        Returns:
            ReasonCode | None: REASON_UNKNOWN_EXTENSION, если расширение
                отсутствует или не было канонизировано, иначе None.
        """
        _ = result  # параметр не используется
        if not self._enabled:
            return None
        return REASON_UNKNOWN_EXTENSION if normalized.ext is None else None
