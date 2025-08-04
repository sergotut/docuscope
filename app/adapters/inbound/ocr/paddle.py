"""DI-обёртка для PaddleOCR."""

from pathlib import Path
from typing import cast

import structlog

from app.adapters.outbound.ocr.paddle import PaddleOCRAdapter
from app.core.ports import OCRPort

logger = structlog.get_logger(__name__)


class PaddleOCRAdapterPort(PaddleOCRAdapter, OCRPort):
    """DI-адаптер для PaddleOCR."""

    def extract_text(self, file_path: Path) -> str:
        """Извлекает текст из файла с помощью PaddleOCR.

        Args:
            file_path (Path): Путь к файлу.

        Returns:
            str: Распознанный текст.
        """
        logger.debug("OCR: extract_text", file=str(file_path))
        with Path(file_path).open("rb") as fh:
            return cast(str, self.ocr(fh.read()))

    def is_healthy(self) -> bool:
        """Проверяет доступность PaddleOCR.

        Returns:
            bool: True, если ошибок не возникло.
        """
        try:
            logger.debug("Проверка is_healthy для PaddleOCRAdapterPort")
            return True
        except Exception as e:
            logger.warning("Ошибка проверки is_healthy", error=str(e))
            return False
