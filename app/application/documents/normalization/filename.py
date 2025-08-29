"""Канонизация расширения файла из имени.

Допускаются пробелы и точки в имени файла. Ограничения применяются только
к самому расширению (последняя часть после точки).
"""

from __future__ import annotations

from app.domain.model.documents import (
    WARN_UNKNOWN_EXTENSION,
    WARN_UNSAFE_EXTENSION_CHARS,
)
from app.domain.shared.codes import WarningCode

__all__ = ["canonical_ext_or_none"]


def canonical_ext_or_none(name: str) -> tuple[str | None, tuple[WarningCode, ...]]:
    """Возвращает каноничное расширение без точки или None и предупреждения.

    Правила канонизации:
    - берётся последняя часть после точки у последнего сегмента имени;
    - нижний регистр;
    - только буквы/цифры любого алфавита, символы '-' и '_';
    - точек, пробелов и разделителей путей быть не должно в самом расширении.

    Args:
        name (str): Исходное имя файла.

    Returns:
        tuple[str | None, tuple[WarningCode, ...]]: Пара (ext, warnings), где
            ext — расширение без точки или None.
    """
    warnings: list[WarningCode] = []

    # Последний сегмент без учёта ОС (и не считая это путём).
    last = name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].strip()

    # Позиция последней точки. Нет точки, точка в начале или в конце — расширения нет.
    dot = last.rfind(".")
    if dot <= 0 or dot == len(last) - 1:
        warnings.append(WARN_UNKNOWN_EXTENSION)
        return None, tuple(warnings)

    ext = last[dot + 1 :].strip().lower()
    if not ext:
        warnings.append(WARN_UNKNOWN_EXTENSION)
        return None, tuple(warnings)

    # В самом расширении не допускаются пробелы/точки/разделители путей.
    if any(ch in "./\\ " for ch in ext) or ext != ext.lower():
        warnings.append(WARN_UNSAFE_EXTENSION_CHARS)
        return None, tuple(warnings)

    # Буквы/цифры любого алфавита + '-' и '_'.
    if not all(ch.isalnum() or ch in "-_" for ch in ext):
        warnings.append(WARN_UNSAFE_EXTENSION_CHARS)
        return None, tuple(warnings)

    return ext, tuple(warnings)
