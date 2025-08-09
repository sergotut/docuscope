"""Адаптер PaddleOCR.

Реализует OCRPort: синхронный и асинхронный методы извлечения текста.
Язык задаётся в DI-провайдере.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import structlog
from paddleocr import PaddleOCR as _PaddleOCR  # type: ignore[import]

from app.core.ports.ocr import OCRPort

logger = structlog.get_logger(__name__)


class PaddleOCR(OCRPort):
    """Общая логика PaddleOCR с фиксированным языком."""

    def __init__(
        self,
        *,
        lang: str,
        use_gpu: bool = False,
        det: bool = True,
        cls: bool = False,
    ) -> None:
        """Инициализирует движок PaddleOCR.

        Args:
            lang (str): Код языка PaddleOCR (ru|eng).
            use_gpu (bool): Использовать ли GPU (CUDA).
            det (bool): Включение детекции текстовых областей.
            cls (bool): Включение классификации ориентации.
        """
        self._engine = _PaddleOCR(
            lang=lang,
            use_gpu=use_gpu,
            show_log=False,
            det=det,
            cls=cls,
        )
        self._lang = lang
        
        logger.info(
            "PaddleOCR init",
            lang=lang,
            use_gpu=use_gpu,
            det=det, cls=cls
        )

    def extract_text(self, file_path: Path) -> str:
        """Распознаёт текст из файла (синхронно).

        Args:
            file_path (Path): Путь к файлу.

        Returns:
            str: Распознанный текст, объединённый через перенос строки.

        Raises:
            TypeError: Если передан не Path.
            FileNotFoundError: Если файл не существует.
        """
        if not isinstance(file_path, Path):
            raise TypeError("file_path must be pathlib.Path")

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        logger.debug("OCR start", path=str(file_path), lang=self._lang)
        raw: list[Any] = self._engine.ocr(str(file_path), cls=False) or []
        lines = self._parse_lines(raw)
        text = "\n".join(lines)
        logger.debug("OCR done", path=str(file_path), lines=len(lines))

        return text

    async def extract_text_async(self, file_path: Path) -> str:
        """Распознаёт текст из файла (асинхронно).

        Args:
            file_path (Path): Путь к изображению или PDF.

        Returns:
            str: Распознанный текст, объединённый через перенос строки.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.extract_text, file_path)

    def is_healthy(self) -> bool:  # noqa: D401
        """Проверяет доступность OCR-движка.

        Returns:
            bool: True, если движок инициализирован и метод ocr доступен.
        """
        try:
            return bool(self._engine and hasattr(self._engine, "ocr"))
        except Exception as exc:  # noqa: BLE001
            return False

    @staticmethod
    def _parse_lines(ocr_result: list[Any]) -> list[str]:
        """Извлекает строки текста из результата PaddleOCR.

        PaddleOCR возвращает результат в формате:
            [
              [ [bbox, (text, conf)], [bbox, (text, conf)], ... ]
            ]

        Args:
            ocr_result (list[Any]): Сырые данные PaddleOCR.

        Returns:
            list[str]: Список распознанных строк.
        """
        if not ocr_result:
            return []

        blocks = ocr_result[0] if isinstance(ocr_result[0], list) else ocr_result
        lines: list[str] = []

        for item in blocks:
            try:
                text = item[1][0]  # item = [bbox, (text, conf)]
            except Exception:  # noqa: BLE001
                logger.warning(
                    "Error in parse line by Paddle OCR",
                    error=str(exc)
                )
                continue
            if isinstance(text, str) and text.strip():
                lines.append(text.strip())
        return lines
