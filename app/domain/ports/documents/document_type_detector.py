"""Порт детекции строгого типа документа."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.model.documents.type_detection import (
    FileProbe,
    TypeDetectionResult
)

__all__ = ["DocumentTypeDetectorPort"]


@runtime_checkable
class DocumentTypeDetectorPort(Protocol):
    """Абстрактный порт детекции строгого типа документа.

    Attributes:
        preferred_head_size: Желаемый объём префикса файла (в байтах), который
            реализация использует для сигнатурного анализа. Используется
            inbound-адаптерами, чтобы сформировать достаточный probe.head.
    """

    preferred_head_size: int

    def detect(self, probe: FileProbe) -> TypeDetectionResult:
        """Определяет тип и возвращает доменный результат.

        Args:
            probe: Минимальные сведения о файле.

        Returns:
            Результат детекции с типом, семейством, допуском, уверенностью
            и предупреждениями.
        """
        ...
