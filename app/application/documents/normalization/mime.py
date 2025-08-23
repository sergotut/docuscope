"""Канонизация MIME-типа."""

from __future__ import annotations

import re

from app.application.documents.detection.codes import (
    WarningCode,
    WARN_INVALID_MIME,
)

__all__ = ["canonical_mime_or_none"]

_MIME_RE = re.compile(r"^[a-z0-9.+-]+/[a-z0-9.+-]+$")


def canonical_mime_or_none(
    mime: str | None,
) -> tuple[str | None, tuple[WarningCode, ...]]:
    """Возвращает каноничный MIME без параметров или None и предупреждения.

    Правила канонизации:
    - обрезаются параметры вида '; charset=utf-8';
    - нижний регистр;
    - проверка формата 'тип/подтип' допустимыми символами.

    Args:
        mime (str | None): MIME-тип от клиента.

    Returns:
        tuple[str | None, tuple[WarningCode, ...]]: Пара (mime, warnings), где
        mime — каноничный MIME или None.
    """
    if not mime:
        return None, ()

    raw = mime.strip().lower()
    main = raw.split(";", 1)[0].strip()

    if not _MIME_RE.fullmatch(main):
        return None, (WARN_INVALID_MIME,)

    return main, ()
