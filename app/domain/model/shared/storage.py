"""Общие типы и модели для объектного хранилища.

Содержит:
- ObjectName — строгий тип имени объекта.
- Blob — неизменяемый бинарный блоб с опциональным оригинальным именем.
- StoredObject — ссылка на сохранённый объект (с expires_at и оригинальным
  именем).
- UploadBatch — результат пакетной загрузки.
- make_object_name — генератор обезличенных уникальных имён.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType

__all__ = [
    "ObjectName",
    "Blob",
    "StoredObject",
    "UploadBatch",
    "make_object_name",
]

ObjectName = NewType("ObjectName", str)
ObjectName.__doc__ = (
    "Строгий тип для имени объекта в хранилище (например, ключ в бакете)."
)


@dataclass(frozen=True, slots=True)
class Blob:
    """Неизменяемая модель бинарного блоба.

    Attributes:
        data (bytes): Сырые байты объекта.
        content_type (str | None): MIME-тип данных, если известен.
        filename (str | None): Оригинальное имя файла на стороне пользователя.
            Используется как метаданные.
    """

    data: bytes
    content_type: str | None = None
    filename: str | None = None

    @property
    def size(self) -> int:
        """Возвращает размер данных в байтах."""
        return len(self.data)


@dataclass(frozen=True, slots=True)
class StoredObject:
    """Ссылка на сохранённый объект.

    Attributes:
        name (ObjectName): Имя объекта в хранилище.
        expires_at (datetime | None): Момент, когда объект станет просроченным.
        original_name (str | None): Оригинальное имя, если известно.
    """

    name: ObjectName
    expires_at: datetime | None = None
    original_name: str | None = None


@dataclass(frozen=True, slots=True)
class UploadBatch:
    """Результат пакетной загрузки объектов.

    Attributes:
        objects (tuple[StoredObject, ...]): Сохранённые объекты в порядке,
            соответствующем входным данным.
    """

    objects: tuple[StoredObject, ...]

    def __len__(self) -> int:
        """Возвращает количество загруженных объектов в батче."""
        return len(self.objects)

    @property
    def names(self) -> tuple[ObjectName, ...]:
        """Возвращает имена всех объектов."""
        return tuple(obj.name for obj in self.objects)


def make_object_name(
    *,
    original_name: str | None,
    now: datetime | None = None,
) -> ObjectName:
    """Генерирует обезличенное уникальное имя объекта.

    Формат:
        YYYY/MM/DD/<uuid4><ext>

    Args:
        original_name (str | None): Оригинальное имя файла. Используется для
            получения расширения.
        now (datetime | None): Время генерации. По умолчанию — текущее UTC.

    Returns:
        ObjectName: Уникальное имя объекта.
    """
    ts = (now or datetime.now(UTC)).strftime("%Y/%m/%d")
    ext = ""
    if original_name:
        _, ext0 = os.path.splitext(original_name)
        ext = ext0.lower() if ext0 and len(ext0) <= 10 else ""
    uid = uuid.uuid4().hex
    return ObjectName(f"{ts}/{uid}{ext}")
