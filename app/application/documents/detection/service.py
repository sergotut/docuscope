"""Сервис принятия решения со склейкой предупреждений и расширяемыми правилами."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.application.documents.detection.codes import (
    ReasonCode,
    WarningCode,
    REASON_FORBIDDEN_BY_DOMAIN,
)
from app.application.documents.detection.options import DocumentDetectionOptions
from app.application.documents.detection.rules import (
    ConfidenceRule,
    DecisionRule,
    ForbiddenByDomainRule,
    MimeExtConflictRule,
    MimeTypeConflictRule,
    UnknownExtensionRule,
)
from app.application.documents.normalization import (
    NormalizedInput,
    normalize_input,
)
from app.domain.model.documents import FileProbe, TypeDetectionResult
from app.domain.ports.documents import DocumentTypeDetectorPort

__all__ = ["DetectionDecision", "DocumentDetectionService"]


@dataclass(frozen=True, slots=True)
class DetectionDecision:
    """Итог прикладного решения.

    Attributes:
        result (TypeDetectionResult): Доменный результат детекции.
        accepted (bool): Принят ли документ приложением.
        reasons (tuple[ReasonCode, ...]): Причины отклонения (если есть).
        warnings (tuple[WarningCode, ...]): Объединённые предупреждения
            из нормализации и детектора.
        normalized (NormalizedInput): Результат нормализации входа (ext/mime).
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
            detector (DocumentTypeDetectorPort): Реализация доменного порта
                детектора типов.
            options (DocumentDetectionOptions | None): Опции прикладного уровня
                (строгость, пороги и т. п.). Если None, используются значения
                по умолчанию.
            rules (Iterable[DecisionRule] | None): Явный набор правил. Если не
                задан, собирается по options.
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
            probe (FileProbe): Проба файла с исходными данными (имя, размер,
                head, заявленный MIME).

        Returns:
            DetectionDecision: Результат детекции, список причин/предупреждений
            и флаг принятия.
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
        normalized: NormalizedInput,
    ) -> DetectionDecision:
        """Детектирует тип и принимает решение, используя уже нормализованный вход.

        Args:
            probe (FileProbe): Проба файла с исходными данными (имя, размер,
                head, заявленный MIME).
            normalized (NormalizedInput): Результаты нормализации имени и MIME.

        Returns:
            DetectionDecision: Результат детекции, список причин/предупреждений
            и флаг принятия.
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
            opt (DocumentDetectionOptions): Опции прикладного уровня.

        Returns:
            tuple[DecisionRule, ...]: Кортеж правил, применяемых по умолчанию.
        """
        rules: list[DecisionRule] = []

        if opt.reject_disallowed_by_domain:
            rules.append(ForbiddenByDomainRule())

        rules.append(ConfidenceRule(min_confidence=opt.min_confidence))
        rules.append(MimeExtConflictRule(enabled=opt.reject_on_mime_extension_conflict))
        rules.append(MimeTypeConflictRule(enabled=opt.reject_on_mime_type_conflict))
        rules.append(UnknownExtensionRule(enabled=opt.reject_on_unknown_extension))

        return tuple(rules)


def _merge_unique(
    a: tuple[WarningCode, ...],
    b: tuple[WarningCode, ...]
) -> tuple[WarningCode, ...]:
    """Объединяет предупреждения без дубликатов, сохраняя порядок появления.

    Args:
        a (tuple[WarningCode, ...]): Предупреждения из нормализации.
        b (tuple[WarningCode, ...]): Предупреждения из детектора.

    Returns:
        tuple[WarningCode, ...]: Предупреждения без повторов,
        в порядке первого появления.
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
        rules (Iterable[DecisionRule]): Набор правил для оценки.
        result (TypeDetectionResult): Доменный результат детекции.
        normalized (NormalizedInput): Результаты нормализации (ext/mime).
        warnings (tuple[WarningCode, ...]): Совмещённые предупреждения
            нормализации и детектора.

    Returns:
        tuple[ReasonCode, ...]: Кортеж кодов причин отклонения. Пустой кортеж
        означает, что отказов нет.
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
        strict (bool): Строгий режим. Если True — отклонять при любой причине.
        reasons (tuple[ReasonCode, ...]): Причины отказа, собранные правилами.

    Returns:
        bool: True, если документ принят; False — если отклонён.
    """
    if strict:
        return not reasons
    # В «мягком» режиме блокируем только доменный запрет.
    return REASON_FORBIDDEN_BY_DOMAIN not in reasons
