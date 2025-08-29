"""DI-адаптеры OCR-движков."""

from .paddle_en import PaddleEnOCRAdapter
from .paddle_ru import PaddleRuOCRAdapter

__all__ = [
    "PaddleRuOCRAdapter",
    "PaddleEnOCRAdapter",
]
