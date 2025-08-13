"""Адаптер PaddleOCR.

Реализует OCRPort: асинхронное распознавание текста из Blob и health-check.
Язык и остальные параметры задаются при инициализации адаптера.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import structlog
from paddleocr import PaddleOCR as _PaddleOCR  # type: ignore[import]

from app.domain.model.media import OcrResult
from app.domain.model.shared import Blob
from app.domain.ports import OCRPort

__all__ = ["PaddleOCR"]

logger = structlog.get_logger(__name__)


class _PaddleEngine(Protocol):
    """Минимальный протокол движка PaddleOCR для mypy."""

    def ocr(self, img_path: str, cls: bool = False) -> list[list[object]]:
        ...


_CONTENT_TYPE_SUFFIX: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "application/pdf": ".pdf",
    "image/tiff": ".tif",
    "image/tif": ".tif",
}


@dataclass(slots=True)
class PaddleOCR(OCRPort):
    """Адаптер поверх PaddleOCR.

    Attributes:
        lang (str): Код языка PaddleOCR (например, ru или en).
        use_gpu (bool): Использовать ли GPU (CUDA).
        det (bool): Включение детекции текстовых областей.
        cls (bool): Включение классификации ориентации.
    """

    lang: str
    use_gpu: bool = False
    det: bool = True
    cls: bool = False

    def __post_init__(self) -> None:
        """Создаёт внутренний движок PaddleOCR и логирует параметры."""
        self._engine: _PaddleEngine = _PaddleOCR(  # type: ignore[call-arg]
            lang=self.lang,
            use_gpu=self.use_gpu,
            show_log=False,
            det=self.det,
            cls=self.cls,
        )
        logger.info(
            "PaddleOCR init",
            lang=self.lang,
            use_gpu=self.use_gpu,
            det=self.det,
            cls=self.cls,
        )

    async def extract_text(self, blob: Blob) -> OcrResult:
        """Распознаёт текст из бинарных данных.

        Args:
            blob (Blob): Двоичные данные и MIME-тип (при наличии).

        Returns:
            OcrResult: Текст построчно, язык и средняя уверенность.
        """
        suffix = self._suffix_from_content_type(blob.content_type)
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix="ocr_"
        ) as f:
            f.write(blob.data)
            tmp_path = Path(f.name)

        try:
            logger.debug("OCR start", path=str(tmp_path), lang=self.lang)

            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(
                None, lambda: self._engine.ocr(str(tmp_path), cls=False)
            )
            lines, confidences = self._parse_lines_and_confidences(raw)
            text = "\n".join(lines)
            avg_conf = (
                sum(confidences) / len(confidences) if confidences else None
            )

            logger.debug(
                "OCR done",
                path=str(tmp_path),
                lines=len(lines),
                avg_confidence=avg_conf,
            )
            return OcrResult(text=text, language=self.lang, confidence=avg_conf)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError as exc:
                logger.warning("OCR temp file cleanup failed", error=str(exc))

    async def is_healthy(self) -> bool:
        """Проверяет доступность OCR-движка.

        Returns:
            bool: True, если движок инициализирован и метод ocr доступен.
        """
        try:
            ok = bool(self._engine and hasattr(self._engine, "ocr"))
            if not ok:
                logger.warning("PaddleOCR health failed: engine not ready")
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.warning("PaddleOCR health exception", error=str(exc))
            return False

    @staticmethod
    def _parse_lines_and_confidences(
        ocr_result: list[object],
    ) -> tuple[list[str], list[float]]:
        """Извлекает строки текста и уверенности из результата PaddleOCR.

        Args:
            ocr_result (list[object]): Сырые данные от движка PaddleOCR.

        Returns:
            tuple[list[str], list[float]]: Пары (строки, уверенности [0..1]).
        """
        if not ocr_result:
            return ([], [])

        blocks = ocr_result[0] if isinstance(ocr_result[0], list) else ocr_result
        lines: list[str] = []
        confs: list[float] = []

        for item in blocks:  # item = [bbox, (text, conf)]
            try:
                pair = item[1]
                text = pair[0]
                conf = pair[1]
            except Exception as exc:  # noqa: BLE001
                logger.warning("PaddleOCR parse error", error=str(exc))
                continue

            if isinstance(text, str):
                stripped = text.strip()
                if stripped:
                    lines.append(stripped)
                    if isinstance(conf, (int, float)):
                        confs.append(float(conf))

        return (lines, confs)

    @staticmethod
    def _suffix_from_content_type(content_type: str | None) -> str:
        """Подбирает расширение временного файла по content-type.

        Args:
            content_type (str | None): MIME-тип данных.

        Returns:
            str: Расширение с точкой (например, .png).
        """
        if not content_type:
            return ".bin"
        ct = content_type.lower().strip()
        return _CONTENT_TYPE_SUFFIX.get(ct, ".bin")
