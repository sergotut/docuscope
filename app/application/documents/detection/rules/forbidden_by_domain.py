"""Правило: доменная политика запретила документ."""

from __future__ import annotations

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_FORBIDDEN_BY_DOMAIN,
)
from app.application.documents.detection.rules.base import DecisionRule
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents import Permission, TypeDetectionResult

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
            result: Доменный результат детекции типа.
            normalized: Нормализованные входные данные (ext/mime).
            warnings: Предупреждения нормализации и/или детектора.

        Returns:
            Причину отклонения REASON_FORBIDDEN_BY_DOMAIN, если документ
            запрещён доменной политикой; иначе None.
        """
        return (
            REASON_FORBIDDEN_BY_DOMAIN
            if result.permission is Permission.FORBIDDEN
            else None
        )
