"""Конвертеры доменных моделей и фильтров в структуры Qdrant."""

from __future__ import annotations

from datetime import UTC, datetime

from qdrant_client.http import models as qm

from app.domain.model.retrieval import (
    AndFilter,
    FieldCondition,
    NotFilter,
    OrFilter,
    QueryFilter,
    SearchHit,
    UpsertPoint,
)

from .models import QdrantDistance
from .utils import DENSE_VECTOR_NAME, PAYLOAD_CREATED_AT_TS, SPARSE_VECTOR_NAME

__all__ = ["to_distance", "to_point_struct", "to_filter", "to_hit"]

ConditionLike = qm.Condition | qm.FieldCondition | qm.IsEmptyCondition


def to_distance(value: str | QdrantDistance) -> qm.Distance:
    """Преобразует метрику в qm.Distance.

    Args:
        value (str | QdrantDistance): cosine | dot | euclid.

    Returns:
        qm.Distance: Соответствующая метрика Qdrant.
    """
    raw = value.value if isinstance(value, QdrantDistance) else value
    n = raw.strip().lower()

    match n:
        case "cos" | "cosine":
            return qm.Distance.COSINE
        case "dot" | "ip" | "inner":
            return qm.Distance.DOT
        case "l2" | "euclid" | "euclidean":
            return qm.Distance.EUCLID
        case _:
            return qm.Distance.COSINE


def to_point_struct(point: UpsertPoint, *, add_created_ts: bool) -> qm.PointStruct:
    """Домашняя точка UpsertPoint → PointStruct Qdrant.

    Args:
        point (UpsertPoint): Точка для вставки/обновления.
        add_created_ts (bool): Добавить отметку времени в payload.

    Returns:
        qm.PointStruct: Структура Qdrant.
    """
    vector: dict[str, list[float]] | None = None
    sparse: dict[str, qm.SparseVector] | None = None

    if point.vector is not None:
        vector = {DENSE_VECTOR_NAME: list(point.vector.values)}

    if point.sparse is not None:
        sparse = {
            SPARSE_VECTOR_NAME: qm.SparseVector(
                indices=list(point.sparse.indices),
                values=list(point.sparse.values),
            )
        }

    payload = dict(point.payload)
    if add_created_ts and PAYLOAD_CREATED_AT_TS not in payload:
        payload[PAYLOAD_CREATED_AT_TS] = int(datetime.now(tz=UTC).timestamp())

    return qm.PointStruct(
        id=str(point.id),
        vector=vector,
        sparse_vectors=sparse,
        payload=payload or None,
    )


def to_filter(flt: QueryFilter) -> qm.Filter:
    """Доменный фильтр → Filter Qdrant.

    Плоские And/Or по простым полям разворачиваются без лишних обёрток.
    Сложные (с вложенными композициями) оборачиваются минимально.
    """
    must: list[ConditionLike] = []
    should: list[ConditionLike] = []
    must_not: list[ConditionLike] = []

    def add_condition(target: list[ConditionLike], f: QueryFilter) -> None:
        match f:
            case FieldCondition():
                target.append(_field_cond(f))
            case _:
                # Вложенная композиция — один раз оборачиваем
                target.append(qm.Condition(filter=to_filter(f)))

    match flt:
        case FieldCondition():
            must.append(_field_cond(flt))

        case AndFilter(filters=fs):
            for f in fs:
                add_condition(must, f)

        case OrFilter(filters=fs):
            for f in fs:
                add_condition(should, f)

        case NotFilter(filter=inner):
            # Оборачиваем всю отрицательную композицию единым узлом
            match inner:
                case FieldCondition():
                    # Прямой not на поле: упрощаем без лишних уровней
                    must_not.append(_field_cond(inner))
                case _:
                    must_not.append(qm.Condition(filter=to_filter(inner)))

        case _:
            # неизвестный тип — пустой фильтр
            ...

    return qm.Filter(
        must=must or None,
        should=should or None,
        must_not=must_not or None,
    )


def _field_cond(fc: FieldCondition) -> ConditionLike:
    """FieldCondition → конкретная Condition-подструктура Qdrant.

    Args:
        fc (FieldCondition): Атомарное условие по полю.

    Returns:
        ConditionLike: Условие для размещения в qm.Filter.
    """
    op = fc.op
    key = fc.field
    val = fc.value

    match op:
        case "eq":
            return qm.FieldCondition(key=key, match=qm.MatchValue(value=val))

        case "ne":
            return qm.Condition(
                must_not=[qm.FieldCondition(key=key, match=qm.MatchValue(value=val))]
            )

        case "in":
            return qm.FieldCondition(key=key, match=qm.MatchAny(any=list(val)))

        case "nin":
            return qm.Condition(
                must_not=[qm.FieldCondition(key=key, match=qm.MatchAny(any=list(val)))]
            )

        case "gt" | "gte" | "lt" | "lte":
            rng = qm.Range(
                gt=val if op == "gt" else None,
                gte=val if op == "gte" else None,
                lt=val if op == "lt" else None,
                lte=val if op == "lte" else None,
            )
            return qm.FieldCondition(key=key, range=rng)

        case "exists":
            present = bool(val)
            return (
                qm.Condition(
                    must_not=[qm.IsEmptyCondition(is_empty=qm.PayloadField(key=key))]
                )
                if present
                else qm.IsEmptyCondition(is_empty=qm.PayloadField(key=key))
            )

        case "match":
            return qm.FieldCondition(key=key, match=qm.MatchText(text=str(val)))

        case _:
            # Неизвестный оператор — безопасно «ничего»
            return qm.Condition()


def to_hit(res: qm.ScoredPoint) -> SearchHit:
    """Конвертирует ScoredPoint Qdrant в доменную модель SearchHit.

    Args:
        res (qm.ScoredPoint): Точка из результата поиска.

    Returns:
        SearchHit: Доменная модель результата.
    """
    return SearchHit(
        id=str(res.id),
        score=float(res.score),
        payload=(res.payload or {}),
    )
