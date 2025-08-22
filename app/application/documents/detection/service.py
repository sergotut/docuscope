"""Сервис принятия решения со склейкой предупреждений и расширяемыми правилами."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.application.documents.detection.codes import ReasonCode, WarningCode
from app.application.documents.detection.options import DocumentDetectionOptions
from app.application.documents.detection.rules import (
    ConfidenceRule,
    DecisionRule,
    ForbiddenByDomainRule,
    MimeExtConflictRule,
    UnknownExtensionRule,
)
from app.application.documents.normalization import (
    NormalizedInput,
    normalize_input
)
from app.domain.model.documents import FileProbe, TypeDetectionResult
from app.domain.ports.documents import DocumentTypeDetectorPort

__all__ = ["DetectionDecision", "DocumentDetectionService"]


@dataclass(frozen=True, slots=True)
class DetectionDecision:
    """Итог прикладного решения.

    Attributes:
        result: Доменный результат детекции.
        accepted: Принят ли документ приложением.
        reasons: Причины отклонения (если есть).
        warnings: Предупреждения из нормализации и детектора, объединённые.
        normalized: Результат нормализации входа (ext/mime).
    """

    result: TypeDetectionResult
    accepted: bool
    reasons: tuple[ReasonCode, ...]
    warnings: tuple[WarningCode, ...]
    normalized: NormalizedInput


class DocumentDetectionService:
    """Применяет прикладные правила и объединяет предупреждения.

    Расширяемость:
    - можно передать собственный набор правил (DecisionRule);
    - по умолчанию используется фабрика из DocumentDetectionOptions;
    - есть метод detect_with_normalized для повторного использования нормализации.
    """

    def __init__(
        self,
        detector: DocumentTypeDetectorPort,
        options: DocumentDetectionOptions | None = None,
        rules: Iterable[DecisionRule] | None = None,
    ) -> None:
        """Инициализирует сервис.

        Args:
            detector: Реализация доменного порта детектора типов.
            options: Опции прикладного уровня (строгость, пороги и т. п.).
            rules: Явный набор правил. Если не задан, собирается по options.
        """
        self._detector = detector
        self._opt = options or DocumentDetectionOptions()
        self._rules = (
            tuple(rules)
            if rules is not None
            else self._make_default_rules(self._opt)
        )
    def detect(self, probe: FileProbe) -> DetectionDecision:
        """Детектирует тип и принимает решение. Самостоятельно нормализует вход.

        Args:
            probe: Проба файла с исходными данными (имя, размер, head, заявленный MIME).

        Returns:
            DetectionDecision с результатом детекции, списком причин/предупреждений
            и флагом принятия.
        """
        norm = normalize_input(
            original_filename=probe.original_filename,
            declared_mime=probe.declared_mime,
        )
        return self.detect_with_normalized(probe=probe, normalized=norm)

    def detect_with_normalized(
        self,
        *,
        probe: FileProbe,
        normalized: NormalizedInput
    ) -> DetectionDecision:
        """Детектирует тип и принимает решение, используя уже нормализованный вход.

        Args:
            probe: Проба файла с исходными данными (имя, размер, head, заявленный MIME).
            normalized: Результаты нормализации имени и MIME.

        Returns:
            DetectionDecision с результатом детекции, списком причин/предупреждений
            и флагом принятия.
        """
        result = self._detector.detect(probe)
        warnings = _merge_unique(normalized.warnings, result.warnings)
        reasons = _collect_reasons(
            self._rules,
            result=result,
            normalized=normalized,
            warnings=warnings
        )
        accepted = _compute_acceptance(strict=self._opt.strict, reasons=reasons)

        return DetectionDecision(
            result=result,
            accepted=accepted,
            reasons=reasons,
            warnings=warnings,
            normalized=normalized,
        )

    @staticmethod
    def _make_default_rules(opt: DocumentDetectionOptions) -> tuple[DecisionRule, ...]:
        """Собирает дефолтный набор правил на основе опций.

        Args:
            opt: Опции прикладного уровня.

        Returns:
            Кортеж правил, применяемых по умолчанию.
        """
        rules: list[DecisionRule] = []

        if opt.reject_disallowed_by_domain:
            rules.append(ForbiddenByDomainRule())

        rules.append(ConfidenceRule(min_confidence=opt.min_confidence))
        rules.append(MimeExtConflictRule(enabled=opt.reject_on_mime_extension_conflict))
        rules.append(UnknownExtensionRule(enabled=opt.reject_on_unknown_extension))

        return tuple(rules)


def _merge_unique(
    a: tuple[WarningCode, ...],
    b: tuple[WarningCode, ...]
) -> tuple[WarningCode, ...]:
    """Объединяет предупреждения без дубликатов, сохраняя порядок появления.

    Args:
        a: Предупреждения из нормализации.
        b: Предупреждения из детектора.

    Returns:
        Кортеж предупреждений без повторов, в порядке первого появления.
    """
    seen: set[WarningCode] = set()
    out: list[WarningCode] = []

    for w in (*a, *b):
        if w not in seen:
            seen.add(w)
            out.append(w)

    return tuple(out)


def _collect_reasons(
    rules: Iterable[DecisionRule],
    *,
    result: TypeDetectionResult,
    normalized: NormalizedInput,
    warnings: tuple[WarningCode, ...],
) -> tuple[ReasonCode, ...]:
    """Вычисляет причины отклонения, последовательно применяя правила.

    Args:
        rules: Набор правил для оценки.
        result: Доменный результат детекции.
        normalized: Результаты нормализации (ext/mime).
        warnings: Совмещённые предупреждения нормализации и детектора.

    Returns:
        Кортеж кодов причин отклонения. Пустой кортеж означает, что отказов нет.
    """
    out: list[ReasonCode] = []

    for rule in rules:
        reason = rule.evaluate(
            result=result,
            normalized=normalized,
            warnings=warnings
        )
        if reason is not None:
            out.append(reason)

    return tuple(out)


def _compute_acceptance(
    *,
    strict: bool,
    reasons: tuple[ReasonCode, ...]
) -> bool:
    """Определяет решение о приёме документа исходя из списка причин.

    Args:
        strict: Строгий режим. Если True — отклонять при любой причине.
        reasons: Причины отказа, собранные правилами.

    Returns:
        True, если документ принят; False — если отклонён.
    """
    if strict:
        return not reasons
    # В «мягком» режиме блокируем только доменный запрет.
    return "forbidden_by_domain" not in reasons
