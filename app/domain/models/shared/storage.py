"""Общие типы и модели для объектного хранилища.

Содержит:
- ObjectName — строгий тип имени объекта.
- Blob — неизменяемый бинарный блоб.
- StoredObject — ссылка на сохранённый объект с опциональным временем истечения.
- UploadBatch — результат пакетной загрузки.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType

__all__ = ["ObjectName", "Blob", "StoredObject", "UploadBatch"]

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
    """

    data: bytes
    content_type: str | None = None

    @property
    def size(self) -> int:
        """Возвращает размер данных в байтах.

        Returns:
            int: Размер data в байтах.
        """
        return len(self.data)


@dataclass(frozen=True, slots=True)
class StoredObject:
    """Ссылка на сохранённый объект.

    Attributes:
        name (ObjectName): Имя объекта в хранилище.
        expires_at (datetime | None): Момент, когда объект станет просроченным.
            Может быть None, если объект бессрочный.
    """

    name: ObjectName
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UploadBatch:
    """Результат пакетной загрузки объектов.

    Attributes:
        objects (tuple[StoredObject, ...]): Сохранённые объекты в порядке
            соответствия входным данным.
    """

    objects: tuple[StoredObject, ...]

    def __len__(self) -> int:
        """Возвращает количество загруженных объектов.

        Returns:
            int: Число элементов в objects.
        """
        return len(self.objects)

    @property
    def names(self) -> tuple[ObjectName, ...]:
        """Возвращает имена всех объектов.

        Returns:
            tuple[ObjectName, ...]: Имена загруженных объектов.
        """
        return tuple(obj.name for obj in self.objects)
