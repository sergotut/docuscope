"""DI-адаптер OCR Paddle Ru.

Подключает движок Paddle Ru через DI.
Использует настройки из конфига.
"""

from __future__ import annotations

import structlog

from app.adapters.outbound import PaddleOCR
from app.infrastructure.config import settings

logger = structlog.get_logger(__name__)


class PaddleRuOCRAdapter(PaddleOCR):
    """Создает русскоязычный OCR-движок Paddle."""

    def __init__(self) -> None:
        """Создает экземпляр с настройками."""

        config = settings.ocr.paddle_ru

        super().__init__(
            lang="ru",
            use_gpu=config.use_gpu,
            det=config.det,
            cls=config.cls,
        )

        logger.info(
            "PaddleRuOCRAdapter init",
            lang="ru",
            use_gpu=config.use_gpu,
            det=config.det,
            cls=config.cls,
        )
