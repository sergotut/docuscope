"""Базовый контракт правила принятия решения.

Определяет минимальный интерфейс правила, которое оценивает доменный результат
детекции и нормализованные входные данные и, при необходимости, возвращает код
причины отклонения.
"""

from __future__ import annotations

from typing import Protocol

from app.application.documents.detection.codes import ReasonCode, WarningCode
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.type_detection import TypeDetectionResult

__all__ = ["DecisionRule"]


class DecisionRule(Protocol):
    """Контракт правила поверх доменного результата.

    Правило не изменяет входные данные и не имеет побочных эффектов.
    Реализации должны быть чистыми и детерминированными.
    """

    def evaluate(
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
        warnings: tuple[WarningCode, ...],
    ) -> ReasonCode | None:
        """Оценивает документ и возвращает причину отклонения либо None.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа
                документа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничное расширение и MIME).
            warnings (tuple[WarningCode, ...]): Объединённые предупреждения
                нормализации и/или детектора.

        Returns:
            ReasonCode | None: Код причины отклонения, если правило считает
            документ неподходящим, иначе None, если правило пройдено.
        """
        ...
