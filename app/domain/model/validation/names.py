"""Общие валидаторы строковых имён и идентификаторов.

Содержит универсальную функцию проверки: непустота, ограничение по длине
и соответствие регулярному выражению.
"""

from __future__ import annotations

from re import Pattern

__all__ = ["validate_name"]


def validate_name(
    value: str,
    *,
    allowed_re: Pattern[str],
    max_len: int,
    kind: str = "Value",
) -> str:
    """Проверяет строковое имя по заданным правилам.

    Args:
        value (str): Исходная строка.
        allowed_re (Pattern[str]): Регулярное выражение допустимых символов.
        max_len (int): Максимально допустимая длина.
        kind (str): Название сущности для сообщений об ошибках.

    Returns:
        str: Нормализованная строка без внешних пробелов.

    Raises:
        ValueError: Если строка пустая, слишком длинная или содержит
            недопустимые символы.
    """
    v = value.strip()

    if not v:
        raise ValueError(f"{kind} не может быть пустым.")

    if len(v) > max_len:
        raise ValueError(f"{kind} превышает допустимую длину {max_len}.")

    if not allowed_re.match(v):
        raise ValueError(
            f"{kind} содержит недопустимые символы. Разрешены: латиница, цифры, "
            "точка, подчёркивание, дефис."
        )

    return v
