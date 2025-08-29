"""Правило: конфликт расширения и детектированного типа.

Логика:
- Берём нормализованное расширение из NormalizedInput.
- Преобразуем расширение в DocumentType с помощью доменного конвертера.
- Если конвертация дала UNKNOWN или расширения нет — правило не срабатывает.
- Если полученный по расширению тип не равен фактическому result.type —
  считаем это конфликтом и возвращаем причину.
"""

from __future__ import annotations

from app.application.documents.detection.reasons import (
    REASON_MIME_EXT_CONFLICT,
    ReasonCode,
)
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents import (
    DocumentType,
    TypeDetectionResult,
    from_extension,
)

__all__ = ["MimeExtConflictRule"]


class MimeExtConflictRule:
    """Отклоняет при несоответствии расширения и детектированного типа."""

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
        """Проверяет соответствие расширения детектированному типу.

        Логика: ext → DocumentType (через from_extension) и сравнение с result.type.
        Неизвестное или отсутствующее расширение не считается конфликтом.

        Args:
            result (TypeDetectionResult): Доменный результат детекции типа.
            normalized (NormalizedInput): Нормализованные входные данные
                (каноничное расширение и MIME).

        Returns:
            ReasonCode | None: REASON_MIME_EXT_CONFLICT при несовпадении типа,
                определённого по расширению, и фактического типа, иначе None.
        """
        if not self._enabled:
            return None

        ext = normalized.ext
        if not ext:
            return None

        ext_type = from_extension(ext)
        if ext_type is DocumentType.UNKNOWN:
            # Неизвестное расширение — решается отдельным правилом.
            return None

        return REASON_MIME_EXT_CONFLICT if ext_type is not result.type else None
