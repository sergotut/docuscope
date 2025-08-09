"""Порт (интерфейс) для распознавания текста (OCR)."""

from pathlib import Path
from typing import Protocol


class OCRPort(Protocol):
    """Абстрактный порт OCR.

    Определяет интерфейс для извлечения текста из файлов и проверки
    доступности сервиса.
    """

    def extract_text(self, file_path: Path) -> str:
        """Извлекает текст из файла синхронно.

        Args:
            file_path (Path): Путь к файлу для распознавания.

        Returns:
            str: Распознанный текст.
        """
        ...

    async def extract_text_async(self, file_path: Path) -> str:
        """Извлекает текст из файла асинхронно.

        Args:
            file_path (Path): Путь к файлу для распознавания.

        Returns:
            str: Распознанный текст.
        """
        ...

    def is_healthy(self) -> bool:
        """Проверяет доступность сервиса OCR.

        Returns:
            bool: True, если сервис доступен.
        """
        ...
