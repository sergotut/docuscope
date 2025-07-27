"""
DI-обёртка для PaddleOCR.
"""

import structlog
from app.adapters.outbound.ocr.paddle import PaddleOCRAdapter
from app.infrastructure.protocols import OCRPort
from pathlib import Path
from typing import cast

logger = structlog.get_logger(__name__)

class PaddleOCRAdapterPort(PaddleOCRAdapter, OCRPort):
    """DI-адаптер для PaddleOCR."""

    def extract_text(self, file_path: Path) -> str:
        logger.debug("OCR: extract_text", file=str(file_path))
        with Path(file_path).open("rb") as fh:
            return cast(str, self.ocr(fh.read()))

    def is_healthy(self) -> bool:
        try:
            logger.debug("Проверка is_healthy для PaddleOCRAdapterPort")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
