"""Утилиты валидации UUID-подобных строк для доменных моделей."""

from __future__ import annotations

import uuid

from app.domain.exceptions import DomainValidationError

__all__ = ["validate_uuid_like"]


def validate_uuid_like(value: str, *, kind: str = "Identifier") -> str:
    """Проверяет, что строка UUID-подобная, и возвращает нормализованное значение.

    Допускаются представления с дефисами и без. Регистр не важен.

    Args:
        value (str): Исходная строка.
        kind (str): Имя сущности для сообщений об ошибках.

    Returns:
        str: Триммированная исходная строка.

    Raises:
        DomainValidationError: Если строка пустая или невалидный UUID.
    """
    v = (value or "").strip()
    if not v:
        raise DomainValidationError(f"{kind} must be a non-empty string.")
    try:
        uuid.UUID(v)
    except ValueError as exc:
        raise DomainValidationError(
            f"{kind} must be a valid UUID (with or without hyphens)."
        ) from exc
    return v
