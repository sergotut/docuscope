"""Геометрические модели для позиционирования контента на страницах."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "BBox",
]


@dataclass(frozen=True, slots=True)
class BBox:
    """Геометрия блока текста или элемента на странице документа.

    Представляет прямоугольную область с координатами и метаданными
    о позиционировании. Используется для восстановления макета
    и сохранения пространственных отношений элементов.

    Attributes:
        page (int | None): Номер страницы (с 1) или None для документов без страниц.
        x0 (float | None): Левая координата прямоугольника.
        y0 (float | None): Верхняя координата прямоугольника.
        x1 (float | None): Правая координата прямоугольника.
        y1 (float | None): Нижняя координата прямоугольника.
        rotation (float | None): Угол поворота элемента в градусах (0-360).
        unit (str | None): Единицы измерения координат ("pt", "px", "mm" и т.п.).
    """

    page: int | None = None
    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None
    rotation: float | None = None
    unit: str | None = None
