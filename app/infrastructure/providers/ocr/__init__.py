"""DI-адаптеры OCR-движков."""

from .paddle_ru import PaddleRuOCRAdapter
from .paddle_en import PaddleEnOCRAdapter


__all__ = [
    "PaddleRuOCRAdapter",
    "PaddleEnOCRAdapter",
]
