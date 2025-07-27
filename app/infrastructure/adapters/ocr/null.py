"""
Null-обёртка для OCR.
"""

import structlog
from app.infrastructure.protocols import OCRPort
from pathlib import Path

logger = structlog.get_logger(__name__)

class NullOCR(OCRPort):
    """Заглушка для OCR."""

    def extract_text(self, file_path: Path) -> str:
        logger.debug("Вызван NullOCR (фолбэк)", file=str(file_path))
        return ""

    def is_healthy(self) -> bool:
        return False
