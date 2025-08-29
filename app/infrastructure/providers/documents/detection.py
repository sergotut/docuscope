"""DI адаптер для Magic детектора типов документов.

Создаёт и настраивает экземпляр MagicDocumentTypeDetector
с параметрами из конфигурации приложения.
"""

from __future__ import annotations

from typing import Callable

import structlog

from app.domain.ports.documents import DocumentTypeDetectorPort
from app.infrastructure.adapters.outbound.documents.document_type_detector import (
    DecisionBasis,
    MagicDetectorTuning,
    MagicDocumentTypeDetector,
)
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)

__all__ = [
    "MagicDocumentTypeDetectorAdapter",
]


class MagicDocumentTypeDetectorAdapter:
    """DI адаптер для создания Magic детектора типов документов.

    Создаёт singleton экземпляр MagicDocumentTypeDetector с настройками
    из конфигурации приложения. Обеспечивает thread-safe доступ и
    оптимальное использование ресурсов.
    """

    _instance: DocumentTypeDetectorPort | None = None

    @classmethod
    def create(cls) -> DocumentTypeDetectorPort:
        """Создаёт или возвращает singleton экземпляр детектора.

        Returns:
            DocumentTypeDetectorPort: Настроенный экземпляр Magic детектора.
        """
        if cls._instance is None:
            cls._instance = cls._create_instance()

        return cls._instance

    @classmethod
    def _create_instance(cls) -> DocumentTypeDetectorPort:
        """Создаёт новый экземпляр Magic детектора с настройками.

        Returns:
            DocumentTypeDetectorPort: Новый экземпляр детектора.
        """
        common_config = settings.documents.common
        detection_config = settings.documents.detection

        # Создаём настройки тюнинга детектора
        tuning = MagicDetectorTuning(
            mime_conflict_penalty=detection_config.mime_conflict_penalty,
            ooxml_confidence_cap=detection_config.ooxml_confidence_cap,
            ole_confidence_cap=detection_config.ole_confidence_cap,
        )

        # Опциональный callback для метрик
        metrics_callback: Callable[[DecisionBasis], None] | None = None
        if common_config.enable_metrics:
            metrics_callback = cls._log_detection_metrics

        detector = MagicDocumentTypeDetector(
            preferred_head_size=common_config.preferred_head_size,
            use_libmagic=detection_config.use_libmagic,
            tuning=tuning,
            on_metrics=metrics_callback,
        )

        logger.info(
            "MagicDocumentTypeDetector created",
            preferred_head_size=common_config.preferred_head_size,
            use_libmagic=detection_config.use_libmagic,
            confidence_threshold=detection_config.confidence_threshold,
            enable_metrics=common_config.enable_metrics,
            scan_limit=int(
                common_config.preferred_head_size
                * detection_config.scan_limit_multiplier
            ),
        )

        return detector

    @staticmethod
    def _log_detection_metrics(basis: DecisionBasis) -> None:
        """Логирует метрики детекции документов.

        Args:
            basis: Базис принятия решения детектором.
        """
        logger.debug(
            "Document detection metrics",
            magic_type=basis.magic_type,
            ext_type=basis.ext_type,
            final_type=basis.final_type,
            confidence=basis.confidence,
        )
