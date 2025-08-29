"""Фасад нормализации входных данных и сборки FileProbe."""

from __future__ import annotations

from dataclasses import dataclass

from app.application.documents.normalization.filename import (
    canonical_ext_or_none,
)
from app.application.documents.normalization.mime import (
    canonical_mime_or_none,
)
from app.domain.model.documents.type_detection import FileProbe
from app.domain.shared.codes import WarningCode

__all__ = [
    "NormalizedInput",
    "normalize_input",
    "build_probe",
]


@dataclass(frozen=True, slots=True)
class NormalizedInput:
    """Результат нормализации входа.

    Attributes:
        ext (str | None): Каноничное расширение без точки или None.
        mime (str | None): Каноничный MIME без параметров или None.
        warnings (tuple[WarningCode, ...]): Предупреждения нормализации.
    """

    ext: str | None
    mime: str | None
    warnings: tuple[WarningCode, ...]


def normalize_input(
    *,
    original_filename: str,
    declared_mime: str | None,
) -> NormalizedInput:
    """Нормализует расширение и MIME.

    Args:
        original_filename (str): Имя файла как пришло от клиента.
        declared_mime (str | None): MIME, заявленный клиентом.

    Returns:
        NormalizedInput: Каноничные значения и предупреждения нормализации.
    """
    ext, w1 = canonical_ext_or_none(original_filename)
    mime, w2 = canonical_mime_or_none(declared_mime)
    return NormalizedInput(ext=ext, mime=mime, warnings=w1 + w2)


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
        original_filename (str): Имя файла от клиента.
        size_bytes (int): Размер файла в байтах.
        head (bytes): Первые N байт файла.
        declared_mime (str | None): MIME от клиента.

    Returns:
        FileProbe: Объект проб файла для передачи в порт детектора.
    """
    name = (original_filename or "").strip()

    norm = normalize_input(
        original_filename=name,
        declared_mime=declared_mime,
    )

    if isinstance(head, bytes):
        head_bytes = head
    elif isinstance(head, (bytearray, memoryview)):
        head_bytes = bytes(head)
    else:
        try:
            head_bytes = bytes(head)  # на случай совместимых буферов
        except Exception as exc:  # noqa: BLE001
            raise TypeError("head должен быть bytes‑подобным") from exc

    try:
        size = int(size_bytes)
    except Exception:  # noqa: BLE001
        size = 0
    if size < 0:
        size = 0

    return FileProbe(
        original_filename=name,
        size_bytes=size,
        head=head_bytes,
        declared_mime=norm.mime,
    )
