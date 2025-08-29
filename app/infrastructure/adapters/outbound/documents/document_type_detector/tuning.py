"""Настройки штрафов и базовых confidence для детектора Magic."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["MagicDetectorTuning"]


@dataclass(frozen=True, slots=True)
class MagicDetectorTuning:
    """Параметры тонкой настройки уверенности.

    Attributes:
        mime_conflict_penalty (float): Сколько вычитать из confidence при
            конфликте заявленного и определённого MIME. Диапазон [0.0..1.0].
        ooxml_confidence_cap (float): Верхняя граница confidence, если OOXML
            подтверждён только расширением/эвристикой. Диапазон [0.0..1.0].
        ole_confidence_cap (float): Верхняя граница confidence, если OLE
            подтверждён только расширением/MIME. Диапазон [0.0..1.0].
        base_signature_confidence (float): База для случая точного совпадения
            по сигнатуре.
        base_zip_container_confidence (float): База для случая ZIP-контейнера
            (DOCX/XLSX), согласованного с расширением.
        base_ole_container_confidence (float): База для случая OLE-контейнера
            (DOC/XLS), согласованного с расширением.
        base_extension_only_confidence (float): База при определении только по
            расширению.
        base_insufficient_evidence_confidence (float): База при недостатке
            данных (UNKNOWN).
    """

    # Штрафы/каппинг
    mime_conflict_penalty: float = 0.05
    ooxml_confidence_cap: float = 0.9
    ole_confidence_cap: float = 0.8

    # Базовые confidence
    base_signature_confidence: float = 0.98
    base_zip_container_confidence: float = 0.85
    base_ole_container_confidence: float = 0.82
    base_extension_only_confidence: float = 0.75
    base_insufficient_evidence_confidence: float = 0.3

    def clamp(self) -> MagicDetectorTuning:
        """Возвращает копию с ограничением значений в диапазоне [0.0..1.0].

        Returns:
            MagicDetectorTuning: Копия с обрезанными в [0.0..1.0] значениями.
        """

        def _clamp01(x: float) -> float:
            if x < 0.0:
                return 0.0
            if x > 1.0:
                return 1.0
            return x

        return MagicDetectorTuning(
            mime_conflict_penalty=_clamp01(self.mime_conflict_penalty),
            ooxml_confidence_cap=_clamp01(self.ooxml_confidence_cap),
            ole_confidence_cap=_clamp01(self.ole_confidence_cap),
            base_signature_confidence=_clamp01(self.base_signature_confidence),
            base_zip_container_confidence=_clamp01(self.base_zip_container_confidence),
            base_ole_container_confidence=_clamp01(self.base_ole_container_confidence),
            base_extension_only_confidence=_clamp01(
                self.base_extension_only_confidence
            ),
            base_insufficient_evidence_confidence=_clamp01(
                self.base_insufficient_evidence_confidence
            ),
        )
