"""
DI-адаптеры OCR.
"""

from .paddle import PaddleOCRAdapterPort
from .null import NullOCR

__all__ = [
    "PaddleOCRAdapterPort",
    "NullOCR",
]
