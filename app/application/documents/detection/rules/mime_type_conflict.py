"""Правило: конфликт заявленного MIME и детектированного строгого типа.

Логика:
- Берётся канонизированный MIME из NormalizedInput.
- Конвертируется MIME в строгий DocumentType (доменный конвертер).
- Если MIME не канонизирован или даёт UNKNOWN — правило не срабатывает.
- Если полученный по MIME тип не равен фактическому result.type —
    считаем это конфликтом и возвращаем причину.
"""

from __future__ import annotations

from app.application.documents.detection.reasons import (
    REASON_MIME_TYPE_CONFLICT,
    ReasonCode,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.converters import from_mimetype
from app.domain.model.documents.type_detection import TypeDetectionResult
from app.domain.model.documents.types import DocumentType

__all__ = ["MimeTypeConflictRule"]


class MimeTypeConflictRule:
    """Проверяет противоречие MIME↔строгий тип."""

    def __init__(self, *, enabled: bool = True) -> None:
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
        """Возвращает REASON_MIME_TYPE_CONFLICT при расхождении MIME↔type.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничный MIME).

        Returns:
            ReasonCode | None: Причина отклонения при конфликте MIME/типа
                либо None, если конфликта нет.
        """
        if not self._enabled:
            return None

        mime = normalized.mime
        if not mime:
            return None

        mime_type = from_mimetype(mime)
        if mime_type is DocumentType.UNKNOWN:
            # Неизвестный/неподдерживаемый MIME — решается другими правилами.
            return None

        return REASON_MIME_TYPE_CONFLICT if mime_type is not result.type else None
