"""Правило: конфликт расширения и детектированного типа.

Логика:
- Берём нормализованное расширение из NormalizedInput.
- Преобразуем расширение в DocumentType с помощью доменного конвертера.
- Если конвертация дала UNKNOWN или расширения нет — правило не срабатывает.
- Если полученный по расширению тип не равен фактическому result.type —
  считаем это конфликтом и возвращаем причину.
"""

from __future__ import annotations

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_MIME_EXT_CONFLICT,
)
from app.application.documents.detection.rules.base import DecisionRule
from app.application.documents.normalization import NormalizedInput
from app.domain.model.documents import (
    DocumentType,
    from_extension,
    TypeDetectionResult
)

__all__ = ["MimeExtConflictRule"]


class MimeExtConflictRule:
    """Отклоняет при несоответствии расширения и детектированного типа."""

    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled

    def evaluate(  # type: ignore[override]
        self,
        *,
        result: TypeDetectionResult,
        normalized: NormalizedInput,
        warnings: tuple[WarningCode, ...],
    ) -> ReasonCode | None:
        """Проверяет соответствие расширения детектированному типу.

        Логика: ext → DocumentType (через from_extension) и сравнение с result.type.
        Неизвестное или отсутствующее расширение не считается конфликтом.

        Args:
            result: Доменный результат детекции типа.
            normalized: Нормализованные входные данные (ext/mime).
            warnings: Предупреждения нормализации и/или детектора.

        Returns:
            Причину отклонения REASON_MIME_EXT_CONFLICT при несовпадении типа
            из расширения и фактического типа иначе None.
        """
        if not self._enabled:
            return None

        ext = normalized.ext
        if not ext:
            return None

        ext_type = from_extension(ext)
        if ext_type is DocumentType.UNKNOWN:
            # Неизвестное расширение — решается отдельным правилом
            #   UnknownExtensionRule.
            return None

        return REASON_MIME_EXT_CONFLICT if ext_type is not result.type else None
