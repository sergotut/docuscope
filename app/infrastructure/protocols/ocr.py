from pathlib import Path
from typing import Protocol


class OCRPort(Protocol):
    """Абстрактный порт OCR."""

    def extract_text(self, file_path: Path) -> str: ...
    def is_healthy(self) -> bool: ...
