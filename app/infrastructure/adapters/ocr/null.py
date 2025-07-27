"""Null-обёртка для OCR."""

from pathlib import Path

import structlog

from app.infrastructure.protocols import OCRPort

logger = structlog.get_logger(__name__)


class NullOCR(OCRPort):
    """Заглушка для OCR."""

    def extract_text(self, file_path: Path) -> str:
        logger.debug("Вызван NullOCR (фолбэк)", file=str(file_path))
        return ""

    def is_healthy(self) -> bool:
        return False
