"""Внутренние модели и конвертеры для работы с MinIO.

Позволяют адаптеру использовать единые структуры независимо от SDK.
Содержат преобразователи из протокольных объектов StatResult и ObjectInfo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, Mapping, cast

from .protocols import ObjectInfo, StatResult

__all__ = [
    "META_EXPIRES_AT",
    "META_ORIGINAL_NAME",
    "ObjectMetadata",
    "HeadObject",
    "ListedObject",
    "meta_from_mapping",
    "mapping_from_meta",
    "head_from_stat",
    "listed_from_info",
]

# Единые ключи кастом-metadata, которые пишет/читает адаптер.
META_EXPIRES_AT: Final[str] = "expires_at"
META_ORIGINAL_NAME: Final[str] = "original-name"


@dataclass(frozen=True, slots=True)
class ObjectMetadata:
    """Типизированные кастом-metadata объекта.

    Attributes:
        expires_at (datetime | None): Время истечения. Если без TZ, считается
            UTC.
        original_name (str | None): Оригинальное имя файла.
        raw (Mapping[str, str]): Исходные метаданные как есть (passthrough).
    """

    expires_at: datetime | None
    original_name: str | None
    raw: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class HeadObject:
    """Нормализованный результат stat_object.

    Attributes:
        content_type (str | None): MIME-тип.
        metadata (ObjectMetadata): Типизированные метаданные.
        size (int | None): Размер в байтах.
        etag (str | None): ETag.
        last_modified (datetime | None): Время модификации.
        version_id (str | None): Версия (если включено версионирование).
        storage_class (str | None): Класс хранения.
    """

    content_type: str | None
    metadata: ObjectMetadata
    size: int | None = None
    etag: str | None = None
    last_modified: datetime | None = None
    version_id: str | None = None
    storage_class: str | None = None


@dataclass(frozen=True, slots=True)
class ListedObject:
    """Элемент списка из list_objects.

    Attributes:
        object_name (str): Полное имя объекта.
        size (int | None): Размер в байтах.
        etag (str | None): ETag.
        last_modified (datetime | None): Время модификации.
        version_id (str | None): Версия объекта.
        is_dir (bool | None): Признак псевдокаталога у некоторых клиентов.
    """

    object_name: str
    size: int | None = None
    etag: str | None = None
    last_modified: datetime | None = None
    version_id: str | None = None
    is_dir: bool | None = None


def _parse_dt(value: str | None) -> datetime | None:
    """Парсит дату-время в формате ISO 8601.

    Если значение без временной зоны, устанавливается UTC.

    Args:
        value (str | None): Строка в формате ISO 8601.

    Returns:
        datetime | None: Разобранное значение или None при ошибке.
    """
    if not value:
        return None

    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)
    except ValueError:
        return None


def meta_from_mapping(mapping: Mapping[str, str]) -> ObjectMetadata:
    """Создаёт ObjectMetadata из словаря кастом-metadata.

    Args:
        mapping (Mapping[str, str]): Сырые метаданные.

    Returns:
        ObjectMetadata: Типизированные метаданные с сохранением исходных
        ключей в raw.
    """
    expires = _parse_dt(mapping.get(META_EXPIRES_AT))
    original = mapping.get(META_ORIGINAL_NAME)
    
    return ObjectMetadata(expires_at=expires, original_name=original, raw=mapping)


def mapping_from_meta(meta: ObjectMetadata) -> dict[str, str]:
    """Создаёт словарь кастом-metadata из ObjectMetadata.

    Args:
        meta (ObjectMetadata): Типизированные метаданные.

    Returns:
        dict[str, str]: Словарь, пригодный для записи в объект.
    """
    d: dict[str, str] = dict(meta.raw)  # сохраняем сторонние ключи
    if meta.expires_at is not None:
        d[META_EXPIRES_AT] = meta.expires_at.isoformat()
    else:
        d.pop(META_EXPIRES_AT, None)

    if meta.original_name:
        d[META_ORIGINAL_NAME] = meta.original_name
    else:
        d.pop(META_ORIGINAL_NAME, None)

    return d


def head_from_stat(stat: StatResult) -> HeadObject:
    """Создаёт HeadObject из StatResult.

    Args:
        stat (StatResult): Результат stat_object.

    Returns:
        HeadObject: Нормализованная модель метаданных объекта.
    """
    raw: Mapping[str, str] = (
        stat.metadata if stat.metadata is not None else cast(Mapping[str, str], {})
    )
    meta = meta_from_mapping(raw)
    size = getattr(stat, "size", None)
    etag = getattr(stat, "etag", None)
    lm = getattr(stat, "last_modified", None)
    ver = getattr(stat, "version_id", None)
    sclass = getattr(stat, "storage_class", None)

    return HeadObject(
        content_type=stat.content_type,
        metadata=meta,
        size=size if isinstance(size, int) else None,
        etag=etag if isinstance(etag, str) else None,
        last_modified=lm if isinstance(lm, datetime) else None,
        version_id=ver if isinstance(ver, str) else None,
        storage_class=sclass if isinstance(sclass, str) else None,
    )


def listed_from_info(info: ObjectInfo) -> ListedObject:
    """Создаёт ListedObject из ObjectInfo.

    Args:
        info (ObjectInfo): Элемент, возвращаемый list_objects.

    Returns:
        ListedObject: Нормализованный элемент списка объектов.
    """
    size = getattr(info, "size", None)
    etag = getattr(info, "etag", None)
    lm = getattr(info, "last_modified", None)
    ver = getattr(info, "version_id", None)
    is_dir = getattr(info, "is_dir", None)

    return ListedObject(
        object_name=info.object_name,
        size=size if isinstance(size, int) else None,
        etag=etag if isinstance(etag, str) else None,
        last_modified=lm if isinstance(lm, datetime) else None,
        version_id=ver if isinstance(ver, str) else None,
        is_dir=is_dir if isinstance(is_dir, bool) else None,
    )
