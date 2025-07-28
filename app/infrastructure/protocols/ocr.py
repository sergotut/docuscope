"""Интерфейс (порт) для распознавания текста (OCR).

Реализуется через адаптеры PaddleOCR, заглушки.
"""

from pathlib import Path
from typing import Protocol


class OCRPort(Protocol):
    """Абстрактный порт OCR.

    Определяет интерфейс для извлечения текста из файлов и проверки доступности.
    """

    def extract_text(self, file_path: Path) -> str:
        """Распознаёт текст из файла.

        Args:
            file_path (Path): Путь к файлу (PDF, PNG, JPEG и т.д.).

        Returns:
            str: Распознанный текст.
        """
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность OCR-модуля.

        Returns:
            bool: True, если OCR работает корректно.
        """
        ...
