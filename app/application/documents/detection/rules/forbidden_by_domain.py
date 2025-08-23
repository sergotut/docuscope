"""Правило: доменная политика запретила документ."""

from __future__ import annotations

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_FORBIDDEN_BY_DOMAIN,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.types import Permission
from app.domain.model.documents.type_detection import TypeDetectionResult

__all__ = ["ForbiddenByDomainRule"]


class ForbiddenByDomainRule:
    """Отклоняет, если доменная политика запрещает документ."""

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
        warnings: tuple[WarningCode, ...],
    ) -> ReasonCode | None:
        """Проверяет запрет доменной политикой.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничное расширение и MIME).
            warnings (tuple[WarningCode, ...]): Предупреждения нормализации
                и/или детектора.

        Returns:
            ReasonCode | None: Причина отклонения REASON_FORBIDDEN_BY_DOMAIN,
            если документ запрещён доменной политикой; иначе None.
        """
        _ = normalized, warnings  # параметры не используются, сигнатура — по протоколу
        return (
            REASON_FORBIDDEN_BY_DOMAIN
            if result.permission is Permission.FORBIDDEN
            else None
        )
