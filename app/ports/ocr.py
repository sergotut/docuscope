""" Порт для OCR-сервисов. """

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class OCRPort(ABC):
    """
    Абстракция извлечения текста из файлов.

    Methods:
        extract_text: Асинхронно извлекает текст из файла.
    """

    @abstractmethod
    async def extract_text(self, file_path: Path) -> str:
        """
        Извлекает текст из файла.

        Args:
            file_path (Path): Путь к файлу (PDF, DOCX, изображение).

        Returns:
            str: Распознанный текст.
        """
        raise NotImplementedError
