"""Детектор типа документов на базе сигнатур и лёгкой инспекции контейнера."""

from __future__ import annotations

from typing import Callable

import structlog

from app.domain.model.documents.converters import (
    from_extension,
    mime_of,
)
from app.domain.model.documents.type_detection import (
    FileProbe,
    TypeDetectionResult,
)
from app.domain.model.documents.types import DocumentType
from app.domain.ports.documents.document_type_detector import (
    DocumentTypeDetectorPort,
)

from ..tuning import MagicDetectorTuning
from ..types import DecisionBasis
from .signatures import has_ole_signature, sniff_magic
from .utils import find_any, norm_ext

__all__ = ["MagicDocumentTypeDetector"]

logger = structlog.get_logger(__name__)


class MagicDocumentTypeDetector(DocumentTypeDetectorPort):
    """Адаптер порта с эвристической детекцией типа документа.

    Возможности:
    - use_libmagic: мягкий fallback к python-magic можно отключить;
    - preferred_head_size: рекомендуемый объём head;
    - tuning: конфигурация штрафов/каппинга и базовых confidence;
    - on_metrics: колбэк для телеметрии основания решения.

    Attributes:
        preferred_head_size (int): Рекомендуемая длина probe.head в байтах.
        _use_libmagic (bool): Разрешать fallback к python-magic.
        _tuning (MagicDetectorTuning): Параметры штрафов/каппинга/базы.
        _on_metrics (Callable[[DecisionBasis], None] | None): Колбэк метрик.
    """

    def __init__(
        self,
        *,
        preferred_head_size: int = 16384,
        use_libmagic: bool = True,
        tuning: MagicDetectorTuning | None = None,
        on_metrics: Callable[[DecisionBasis], None] | None = None,
    ) -> None:
        """Создаёт экземпляр детектора.

        Args:
            preferred_head_size (int): Рекомендуемая длина probe.head в байтах.
                Значение приводится к int и ограничивается снизу 0.
            use_libmagic (bool): Включать ли fallback к python-magic, если
                установлен.
            tuning (MagicDetectorTuning | None): Параметры штрафов/каппинга и
                базовых confidence. Если None, используются значения по умолчанию.
            on_metrics (Callable[[DecisionBasis], None] | None): Колбэк,
                принимающий основание решения.
        """
        size = int(preferred_head_size)
        if size < 0:
            logger.warning(
                "preferred_head_size_below_zero",
                was=preferred_head_size,
                used=0,
            )
            size = 0

        self._preferred_head_size = size
        self._use_libmagic = bool(use_libmagic)
        self._tuning = (tuning or MagicDetectorTuning()).clamp()
        self._on_metrics = on_metrics

    def detect(self, probe: FileProbe) -> TypeDetectionResult:
        """Определяет тип документа и возвращает доменный результат.

        Args:
            probe (FileProbe): Проба файла (исходное имя, размер, head,
                заявленный MIME).

        Returns:
            TypeDetectionResult: Итоговый тип/семейство, MIME, уверенность и
                предупреждения.
        """
        name = probe.original_filename
        ext = norm_ext(name)
        declared_mime = (probe.declared_mime or "").lower() or None

        notes: list[str] = []

        # Тип по расширению из доменного конвертера
        ext_type_raw = from_extension(ext) if ext else DocumentType.UNKNOWN
        ext_type = None if ext_type_raw is DocumentType.UNKNOWN else ext_type_raw

        magic_type, magic_mime, magic_notes = sniff_magic(
            probe.head,
            use_libmagic=self._use_libmagic,
            scan_limit=self._preferred_head_size,
        )
        if magic_notes:
            notes.extend(magic_notes)

        final_type, final_mime, notes, confidence, basis = self._choose_type(
            magic_type=magic_type,
            magic_mime=(magic_mime or None),
            ext_type=ext_type,
            declared_mime=declared_mime,
            notes=notes,
        )

        # Телеметрия
        self._emit_metrics(basis)

        # Конфликт заявленного и определённого MIME → штраф
        if declared_mime and final_mime and declared_mime != final_mime:
            notes.append("mime_conflict:declared_vs_detected")
            confidence = max(
                0.0,
                confidence - self._tuning.mime_conflict_penalty,
            )

        # OOXML подтверждён только эвристикой — каппим confidence
        if final_type in (
            DocumentType.WORD_DOCX,
            DocumentType.EXCEL_XLSX,
        ) and not find_any(
            probe.head,
            (b"word/", b"xl/"),
            limit=self._preferred_head_size,
        ):
            notes.append("ooxml_by_extension_or_mime")
            confidence = min(confidence, self._tuning.ooxml_confidence_cap)

        # OLE подтверждён только расширением/MIME — каппим confidence
        if final_type in (
            DocumentType.WORD_DOC,
            DocumentType.EXCEL_XLS,
        ) and not has_ole_signature(probe.head):
            notes.append("ole_by_extension_or_mime")
            confidence = min(confidence, self._tuning.ole_confidence_cap)

        return TypeDetectionResult.make(
            type_=final_type,
            ext=ext,
            mime=final_mime or declared_mime,
            confidence=confidence,
            warnings=tuple(notes),
        )

    @property
    def preferred_head_size(self) -> int:
        """Рекомендуемая длина probe.head в байтах (read-only).

        Returns:
            int: Рекомендуемая длина probe.head в байтах.
        """
        return self._preferred_head_size

    def _choose_type(
        self,
        *,
        magic_type: DocumentType | None,
        magic_mime: str | None,
        ext_type: DocumentType | None,
        declared_mime: str | None,
        notes: list[str],
    ) -> tuple[DocumentType, str | None, list[str], float, DecisionBasis]:
        """Определяет итоговый тип по сигнатуре, расширению и заявленному MIME.

        Args:
            magic_type (DocumentType | None): Тип, извлечённый по сигнатурам.
            magic_mime (str | None): MIME, извлечённый по сигнатурам.
            ext_type (DocumentType | None): Тип, определённый по расширению.
            declared_mime (str | None): MIME, заявленный клиентом.
            notes (list[str]): Аккумулируемый список пометок/предупреждений.

        Returns:
            tuple[DocumentType, str | None, list[str], float, DecisionBasis]:
                Итоговый тип, итоговый MIME, заметки, confidence и основание.
        """
        t = self._tuning

        # 1) Точный тип по сигнатурам
        if magic_type is not None:
            mime = mime_of(magic_type) or (magic_mime or None)
            return (
                magic_type,
                mime,
                notes,
                t.base_signature_confidence,
                "signature_match",
            )

        # 2) Согласование контейнера и расширения (ZIP/OLE)
        if magic_mime and ext_type is not None:
            is_zip = magic_mime.startswith("application/zip")
            is_ole = magic_mime in (
                "application/x-ole-storage",
                "application/octet-stream",
            )
            if is_zip and ext_type in (
                DocumentType.WORD_DOCX,
                DocumentType.EXCEL_XLSX,
            ):
                return (
                    ext_type,
                    (mime_of(ext_type) or magic_mime),
                    notes,
                    t.base_zip_container_confidence,
                    "container_hint",
                )
            if is_ole and ext_type in (
                DocumentType.WORD_DOC,
                DocumentType.EXCEL_XLS,
            ):
                notes.append("ole_extension_consistent")
                return (
                    ext_type,
                    (mime_of(ext_type) or magic_mime),
                    notes,
                    t.base_ole_container_confidence,
                    "container_hint",
                )

        # 3) Есть только расширение — используем его как кандидат
        if ext_type is not None:
            mime = mime_of(ext_type) or (magic_mime or declared_mime)
            return (
                ext_type,
                mime,
                notes,
                t.base_extension_only_confidence,
                "extension_only",
            )

        # 4) Недостаточно данных — UNKNOWN
        return (
            DocumentType.UNKNOWN,
            declared_mime or magic_mime,
            notes,
            t.base_insufficient_evidence_confidence,
            "insufficient_evidence",
        )

    def _emit_metrics(self, basis: DecisionBasis) -> None:
        """Передаёт основание решения во внешний колбэк метрик.

        Args:
            basis (DecisionBasis): Основание решения.
        """
        cb = self._on_metrics
        if cb is None:
            return
        try:
            cb(basis)
        except Exception:  # noqa: BLE001
            logger.exception("metrics_callback_failed", basis=basis)
