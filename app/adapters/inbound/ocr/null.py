"""Null-обёртка для OCR."""

from pathlib import Path

import structlog

from app.core.ports import OCRPort

logger = structlog.get_logger(__name__)


class NullOCR(OCRPort):
    """Заглушка для OCR.

    Используется при отключённой системе распознавания текста.
    """

    def extract_text(self, file_path: Path) -> str:
        """Возвращает пустую строку вместо текста.

        Args:
            file_path (Path): Путь к файлу (PDF/изображение).

        Returns:
            str: Пустая строка.
        """
        logger.debug("Вызван NullOCR (фолбэк)", file=str(file_path))
        return ""

    def is_healthy(self) -> bool:
        """Всегда возвращает False (OCR неактивен).

        Returns:
            bool: False
        """
        return False
