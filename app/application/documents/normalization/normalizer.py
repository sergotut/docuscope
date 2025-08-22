"""Фасад нормализации входных данных и сборки FileProbe."""

from __future__ import annotations

from dataclasses import dataclass

from app.application.documents.detection import WarningCode
from app.application.documents.normalization import (
    canonical_ext_or_none,
    canonical_mime_or_none
)
from app.domain.model.documents.type_detection import FileProbe

__all__ = [
    "NormalizedInput",
    "normalize_input",
    "build_probe"
]


@dataclass(frozen=True, slots=True)
class NormalizedInput:
    """Результат нормализации входа.

    Attributes:
        ext: Каноничное расширение без точки или None.
        mime: Каноничный MIME без параметров или None.
        warnings: Предупреждения нормализации.
    """

    ext: str | None
    mime: str | None
    warnings: tuple[WarningCode, ...]


def normalize_input(
    *,
    original_filename: str,
    declared_mime: str | None
) -> NormalizedInput:
    """Нормализует расширение и MIME.

    Args:
        original_filename: Имя файла как пришло от клиента.
        declared_mime: MIME, заявленный клиентом.

    Returns:
        NormalizedInput с каноничными значениями и предупреждениями.
    """
    ext, w1 = canonical_ext_or_none(original_filename)
    mime, w2 = canonical_mime_or_none(declared_mime)
    return NormalizedInput(ext=ext, mime=mime, warnings=tuple((*w1, *w2)))


def build_probe(
    *,
    original_filename: str,
    size_bytes: int,
    head: bytes,
    declared_mime: str | None,
) -> FileProbe:
    """Создаёт FileProbe с нормализованным MIME.

    Нормализованный ext используется на уровне application, в FileProbe не кладётся.

    Args:
        original_filename: Имя файла от клиента.
        size_bytes: Размер файла в байтах.
        head: Первые N байт файла.
        declared_mime: MIME от клиента.

    Returns:
        FileProbe для передачи в порт детектора.
    """
    norm = normalize_input(
        original_filename=original_filename,
        declared_mime=declared_mime
    )

    return FileProbe(
        original_filename=original_filename,
        size_bytes=size_bytes,
        head=head,
        declared_mime=norm.mime,
    )
