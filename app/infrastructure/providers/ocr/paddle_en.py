"""DI-адаптер OCR Paddle En.

Подключает движок Paddle En через DI.
Использует настройки из конфига.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import PaddleOCR
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class PaddleEnOCRAdapter(PaddleOCR):
    """Создает англоязычный OCR-движок Paddle."""

    def __init__(self) -> None:
        """Создает экземпляр с настройками."""

        config = settings.ocr.paddle_en

        super().__init__(
            lang="en",
            use_gpu=config.use_gpu,
            det=config.det,
            cls=config.cls,
        )

        logger.info(
            "PaddleEnOCRAdapter init",
            lang="en",
            use_gpu=config.use_gpu,
            det=config.det,
            cls=config.cls,
        )
