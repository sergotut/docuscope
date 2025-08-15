"""Доменные модели фильтров для поиска в векторном хранилище.

Поддерживаются атомарные сравнения по полям и логические композиции.
Адаптеры векторных БД сами маппят эти структуры в формат движка.

Также предоставлены конструкторы-функции (builder API), чтобы собирать фильтры
удобно и типобезопасно: eq, ne, gt, gte, lt, lte, isin, nin, exists, match,
and_, or_, not_.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Sequence, Union

__all__ = [
    "FieldCondition",
    "AndFilter",
    "OrFilter",
    "NotFilter",
    "QueryFilter",
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "isin",
    "nin",
    "exists",
    "match",
    "and_",
    "or_",
    "not_",
]

Op = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "exists", "match"]


@dataclass(frozen=True, slots=True)
class FieldCondition:
    """Атомарное условие по полю.

    Attributes:
        field (str): Имя поля в payload.
        op (Op): Оператор сравнения.
        value (Any): Значение сравнения. Для in/nin — последовательность,
            для exists — bool, для match — строка термина/шаблона.
    """

    field: str
    op: Op
    value: Any


@dataclass(frozen=True, slots=True)
class AndFilter:
    """Логическое И над списком фильтров.

    Attributes:
        filters (tuple[QueryFilter, ...]): Набор дочерних фильтров.
    """

    filters: tuple["QueryFilter", ...]


@dataclass(frozen=True, slots=True)
class OrFilter:
    """Логическое ИЛИ над списком фильтров.

    Attributes:
        filters (tuple[QueryFilter, ...]): Набор дочерних фильтров.
    """

    filters: tuple["QueryFilter", ...]


@dataclass(frozen=True, slots=True)
class NotFilter:
    """Логическое НЕ для одного фильтра.

    Attributes:
        filter (QueryFilter): Дочерний фильтр.
    """

    filter: "QueryFilter"


QueryFilter = Union[FieldCondition, AndFilter, OrFilter, NotFilter]


def eq(field: str, value: Any) -> FieldCondition:
    """Условие равенства.

    Args:
        field (str): Имя поля.
        value (Any): Ожидаемое значение.

    Returns:
        FieldCondition: Фильтр field == value.
    """
    return FieldCondition(field=field, op="eq", value=value)


def ne(field: str, value: Any) -> FieldCondition:
    """Условие неравенства.

    Args:
        field (str): Имя поля.
        value (Any): Значение для сравнения.

    Returns:
        FieldCondition: Фильтр field != value.
    """
    return FieldCondition(field=field, op="ne", value=value)


def gt(field: str, value: Any) -> FieldCondition:
    """Больше (строго).

    Args:
        field (str): Имя поля.
        value (Any): Нижняя граница (исключая).

    Returns:
        FieldCondition: Фильтр field > value.
    """
    return FieldCondition(field=field, op="gt", value=value)


def gte(field: str, value: Any) -> FieldCondition:
    """Больше или равно.

    Args:
        field (str): Имя поля.
        value (Any): Нижняя граница (включая).

    Returns:
        FieldCondition: Фильтр field >= value.
    """
    return FieldCondition(field=field, op="gte", value=value)


def lt(field: str, value: Any) -> FieldCondition:
    """Меньше (строго).

    Args:
        field (str): Имя поля.
        value (Any): Верхняя граница (исключая).

    Returns:
        FieldCondition: Фильтр field < value.
    """
    return FieldCondition(field=field, op="lt", value=value)


def lte(field: str, value: Any) -> FieldCondition:
    """Меньше или равно.

    Args:
        field (str): Имя поля.
        value (Any): Верхняя граница (включая).

    Returns:
        FieldCondition: Фильтр field <= value.
    """
    return FieldCondition(field=field, op="lte", value=value)


def isin(field: str, values: Sequence[Any] | Iterable[Any]) -> FieldCondition:
    """Вхождение в набор (аналог IN).

    Args:
        field (str): Имя поля.
        values (Sequence[Any] | Iterable[Any]): Набор допустимых значений.

    Returns:
        FieldCondition: Фильтр field in values.
    """
    return FieldCondition(field=field, op="in", value=list(values))


def nin(field: str, values: Sequence[Any] | Iterable[Any]) -> FieldCondition:
    """Не в наборе (NOT IN).

    Args:
        field (str): Имя поля.
        values (Sequence[Any] | Iterable[Any]): Набор исключаемых значений.

    Returns:
        FieldCondition: Фильтр field not in values.
    """
    return FieldCondition(field=field, op="nin", value=list(values))


def exists(field: str, present: bool = True) -> FieldCondition:
    """Проверка существования поля.

    Args:
        field (str): Имя поля.
        present (bool): True — поле должно существовать, False — отсутствовать.

    Returns:
        FieldCondition: Фильтр на существование поля.
    """
    return FieldCondition(field=field, op="exists", value=present)


def match(field: str, term: str) -> FieldCondition:
    """Текстовое совпадение/поиск.

    Args:
        field (str): Имя поля.
        term (str): Текстовый термин/шаблон.

    Returns:
        FieldCondition: Фильтр текстового совпадения.
    """
    return FieldCondition(field=field, op="match", value=term)


def and_(*filters: QueryFilter) -> AndFilter:
    """Логическое И над набором фильтров.

    Args:
        *filters (QueryFilter): Дочерние фильтры.

    Returns:
        AndFilter: Композитный фильтр.
    """
    return AndFilter(filters=tuple(filters))


def or_(*filters: QueryFilter) -> OrFilter:
    """Логическое ИЛИ над набором фильтров.

    Args:
        *filters (QueryFilter): Дочерние фильтры.

    Returns:
        OrFilter: Композитный фильтр.
    """
    return OrFilter(filters=tuple(filters))


def not_(filter: QueryFilter) -> NotFilter:
    """Логическое НЕ.

    Args:
        filter (QueryFilter): Дочерний фильтр.

    Returns:
        NotFilter: Инвертированный фильтр.
    """
    return NotFilter(filter=filter)
