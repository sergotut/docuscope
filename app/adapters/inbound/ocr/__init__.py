"""DI-адаптеры OCR."""

from .null import NullOCR
from .paddle import PaddleOCRAdapterPort

__all__ = [
    "PaddleOCRAdapterPort",
    "NullOCR",
]
