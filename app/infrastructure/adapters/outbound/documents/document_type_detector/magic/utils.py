"""Утилиты для адаптера детекции типа документов."""

from __future__ import annotations

import os
from typing import Iterable


def norm_ext(filename: str | os.PathLike[str]) -> str | None:
    """Извлекает расширение файла из имени.

    Возвращает значение без точки в нижнем регистре или None, если расширение
    отсутствует. Точка в начале имени (например, .env) также считается
    разделителем, то есть для .env вернётся env.

    Args:
        filename (str | os.PathLike[str]): Имя файла. Может включать путь и
            несколько точек.

    Returns:
        str | None: Расширение без точки в нижнем регистре или None.
    """
    name = os.fspath(filename).strip().lower()
    if "." not in name:
        return None
    ext = name.rsplit(".", 1)[-1]
    return ext or None


def find_any(buf: bytes, needles: Iterable[bytes], limit: int | None = None) -> bool:
    """Проверяет наличие хотя бы одной подпоследовательности в первых N байтах.

    Поиск выполняется по буферу без регулярных выражений и без декомпрессии
    входных данных. Срез исходных данных не создаётся.

    Args:
        buf (bytes): Байтовый буфер содержимого файла.
        needles (Iterable[bytes]): Подпоследовательности байт для поиска.
            Пустые подпоследовательности игнорируются.
        limit (int | None): Максимальное число начальных байт для просмотра.
            Если None, используется верхняя граница в 16384 байт. Фактический
            лимит всегда ограничивается диапазоном от 0 до 16384.

    Returns:
        bool: True, если найдена хотя бы одна подпоследовательность; иначе False.
    """
    # 16 KiB — верхний предел объёма данных, в котором выполняется поиск.
    maxlen = 16384 if limit is None else max(0, min(limit, 16384))
    if maxlen == 0:
        return False

    for n in needles:
        if not n:
            continue
        if buf.find(n, 0, maxlen) != -1:
            return True
    return False
