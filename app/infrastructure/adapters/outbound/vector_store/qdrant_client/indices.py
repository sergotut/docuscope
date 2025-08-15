"""Внутренние хелперы по управлению payload-индексами в Qdrant.

Реализует декларативное создание/удаление индексов по полям payload, а также
утилиты для проверки и перечисления существующих индексов.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm

from app.domain.model.vector_store import CollectionName, FieldName
from .models import (
    QdrantKeywordIndexSpec,
    QdrantTextIndexConfig,
    QdrantTextIndexSpec
)
from .utils import as_collection_name, as_field_name

__all__ = [
    "IndexSpec",
    "list_payload_indexes",
    "has_payload_index",
    "ensure_keyword_index",
    "ensure_text_index",
    "ensure_indexes",
    "ensure_indexes_for_many",
    "drop_payload_index",
]

IndexSpec = QdrantKeywordIndexSpec | QdrantTextIndexSpec


async def list_payload_indexes(
    client: AsyncQdrantClient,
    collection: CollectionName | str,
) -> dict[str, Any]:
    """Возвращает схему payload-полей коллекции.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        collection (CollectionName | str): Имя коллекции.

    Returns:
        dict[str, Any]: Словарь со схемой полей payload. Пустой, если нет.
    """
    info = await client.get_collection(as_collection_name(collection))
    schema = getattr(info, "payload_schema", None)

    if not schema:
        return {}

    return cast(dict[str, Any], dict(schema))


async def has_payload_index(
    client: AsyncQdrantClient,
    collection: CollectionName | str,
    field: FieldName | str,
) -> bool:
    """Проверяет, есть ли индекс/схема для поля.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        collection (CollectionName | str): Имя коллекции.
        field (FieldName | str): Имя поля payload.

    Returns:
        bool: True, если индекс для поля уже существует.
    """
    schema = await list_payload_indexes(client, collection)
    return as_field_name(field) in schema


async def ensure_keyword_index(
    client: AsyncQdrantClient,
    collection: CollectionName | str,
    field: FieldName | str,
) -> None:
    """Создаёт keyword-индекс, если его нет.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        collection (CollectionName | str): Имя коллекции.
        field (FieldName | str): Имя поля payload.
    """
    if await has_payload_index(client, collection, field):
        return

    await client.create_payload_index(
        collection_name=as_collection_name(collection),
        field_name=as_field_name(field),
        field_schema=qm.PayloadSchemaType.KEYWORD,
    )


async def ensure_text_index(
    client: AsyncQdrantClient,
    collection: CollectionName | str,
    field: FieldName | str,
    *,
    tokenizer: str = "word",
    min_token_len: int = 2,
    max_token_len: int = 20,
    lowercase: bool = True,
) -> None:
    """Создаёт text-индекс для поля, если его нет.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        collection (CollectionName | str): Имя коллекции.
        field (FieldName | str): Имя поля payload.
        tokenizer (str): Тип токенизации: word, space, prefix.
        min_token_len (int): Минимальная длина токена.
        max_token_len (int): Максимальная длина токена.
        lowercase (bool): Приводить ли текст к нижнему регистру.
    """
    if await has_payload_index(client, collection, field):
        return

    schema: qm.TextIndexParams = qm.TextIndexParams(
        type="text",
        tokenizer=_to_tokenizer(tokenizer),
        min_token_len=min_token_len,
        max_token_len=max_token_len,
        lowercase=lowercase,
    )

    await client.create_payload_index(
        collection_name=as_collection_name(collection),
        field_name=as_field_name(field),
        field_schema=schema,
    )


async def ensure_indexes(
    client: AsyncQdrantClient,
    collection: CollectionName | str,
    specs: Iterable[IndexSpec],
) -> None:
    """Пакетно создаёт индексы по декларативным спецификациям.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        collection (CollectionName | str): Имя коллекции.
        specs (Iterable[IndexSpec]): Набор спецификаций индексов.
    """
    for spec in specs:
        if isinstance(spec, QdrantKeywordIndexSpec):
            await ensure_keyword_index(client, collection, spec.field)
        else:
            cfg: QdrantTextIndexConfig = spec.config
            await ensure_text_index(
                client,
                collection,
                spec.field,
                tokenizer=cfg.tokenizer,
                min_token_len=cfg.min_token_len,
                max_token_len=cfg.max_token_len,
                lowercase=cfg.lowercase,
            )


async def ensure_indexes_for_many(
    client: AsyncQdrantClient,
    plan: Mapping[CollectionName | str, Iterable[IndexSpec]],
) -> None:
    """Создаёт индексы сразу для нескольких коллекций.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        plan (Mapping[CollectionName | str, Iterable[IndexSpec]]): Карта
            коллекций и спецификаций индексов.
    """
    for collection, specs in plan.items():
        await ensure_indexes(client, collection, specs)


async def drop_payload_index(
    client: AsyncQdrantClient,
    collection: CollectionName | str,
    field: FieldName | str,
) -> None:
    """Удаляет индекс/схему поля, если она есть.

    Args:
        client (AsyncQdrantClient): Клиент Qdrant.
        collection (CollectionName | str): Имя коллекции.
        field (FieldName | str): Имя поля payload.
    """
    if not await has_payload_index(client, collection, field):
        return
    await client.delete_payload_index(
        collection_name=as_collection_name(collection),
        field_name=as_field_name(field),
    )


def _to_tokenizer(name: str) -> qm.TokenizerType:
    """Маппит строку в TokenizerType с безопасным дефолтом.

    Args:
        name (str): Имя токенизатора (word/space/prefix, допускаются алиасы).

    Returns:
        qm.TokenizerType: Тип токенизатора для Qdrant.
    """
    n = name.strip().lower()
    match n:
        case "word" | "words":
            return qm.TokenizerType.WORD
        case "space" | "whitespace":
            return qm.TokenizerType.SPACE
        case "prefix" | "ngram" | "n-gram":
            return qm.TokenizerType.PREFIX
        case _:
            return qm.TokenizerType.WORD