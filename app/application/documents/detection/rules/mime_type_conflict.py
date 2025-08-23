"""Правило: конфликт заявленного MIME и детектированного строгого типа.

Логика:
- Берётся канонизированный MIME из NormalizedInput.
- Конвертируется MIME в строгий DocumentType (доменный конвертер).
- Если MIME не канонизирован или даёт UNKNOWN — правило не срабатывает.
- Если полученный по MIME тип не равен фактическому result.type —
  считаем это конфликтом и возвращаем причину.
"""

from __future__ import annotations

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_MIME_TYPE_CONFLICT,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents.converters import from_mimetype
from app.domain.model.documents.types import DocumentType
from app.domain.model.documents.type_detection import TypeDetectionResult

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
        warnings: tuple[WarningCode, ...],
    ) -> ReasonCode | None:
        """Возвращает REASON_MIME_TYPE_CONFLICT при расхождении MIME↔type.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничный MIME).
            warnings (tuple[WarningCode, ...]): Предупреждения нормализации
                и/или детектора.

        Returns:
            ReasonCode | None: Причина отклонения при конфликте MIME/типа
            либо None, если конфликта нет.
        """
        _ = warnings  # параметр не используется; сигнатура — по протоколу
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
