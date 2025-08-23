"""Опции принятия решения поверх результата детекции."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["DocumentDetectionOptions"]


@dataclass(frozen=True, slots=True)
class DocumentDetectionOptions:
    """Правила прикладного слоя.

    Attributes:
        strict (bool): Если True, отклонять при любых накопленных причинах.
        min_confidence (float): Минимально допустимая уверенность 0.0..1.0.
        reject_on_mime_extension_conflict (bool): Отклонять при конфликте
            MIME и расширения.
        reject_on_unknown_extension (bool): Отклонять при отсутствии расширения.
        reject_disallowed_by_domain (bool): Отклонять, если доменная политика
            запрещает тип.
    """

    strict: bool = False
    min_confidence: float = 0.55
    reject_on_mime_extension_conflict: bool = True
    reject_on_mime_type_conflict: bool = True
    reject_on_unknown_extension: bool = False
    reject_disallowed_by_domain: bool = True

    def __post_init__(self) -> None:
        """Проверяет инварианты значений опций.

        Raises:
            ValueError: Если min_confidence вне диапазона 0.0..1.0.
        """
        if not (0.0 <= self.min_confidence <= 1.0):
            raise ValueError("min_confidence должен быть в диапазоне 0.0..1.0")
