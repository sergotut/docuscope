"""DI providers для работы с документами.

Содержит адаптеры для инъекции зависимостей детекторов и конвертеров документов.
"""

from __future__ import annotations

from .conversion import LibreOfficeDocumentConverterAdapter
from .detection import MagicDocumentTypeDetectorAdapter

__all__ = [
    "MagicDocumentTypeDetectorAdapter",
    "LibreOfficeDocumentConverterAdapter",
]
