"""Правило: доменная политика запретила документ."""

from __future__ import annotations

from app.application.documents.detection.reasons import (
    REASON_FORBIDDEN_BY_DOMAIN,
    ReasonCode,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.type_detection import TypeDetectionResult
from app.domain.model.documents.types import Permission

__all__ = ["ForbiddenByDomainRule"]


class ForbiddenByDomainRule:
    """Отклоняет, если доменная политика запрещает документ."""

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
    ) -> ReasonCode | None:
        """Проверяет запрет доменной политикой.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничное расширение и MIME).

        Returns:
            ReasonCode | None: Причина отклонения REASON_FORBIDDEN_BY_DOMAIN,
                если документ запрещён доменной политикой, иначе None.
        """
        _ = normalized  # параметр не используется
        return (
            REASON_FORBIDDEN_BY_DOMAIN
            if result.permission is Permission.FORBIDDEN
            else None
        )
