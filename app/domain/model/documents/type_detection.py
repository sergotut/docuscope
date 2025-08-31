"""Value-объекты для детекции типа документа."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.exceptions import DomainValidationError
from app.domain.model.documents.types import (
    DocumentFamily,
    DocumentType,
    Permission,
    family_of,
    permission_of,
)

__all__ = [
    "FileProbe",
    "TypeDetectionResult",
]


@dataclass(frozen=True, slots=True)
class FileProbe:
    """Минимальные сведения о файле для детектора типа.

    Attributes:
        original_filename (str): Имя файла от пользователя.
        size_bytes (int): Размер в байтах (>= 0).
        head (bytes): Первые N байт для сигнатурного анализа.
        declared_mime (str | None): MIME, заявленный клиентом.
    """

    original_filename: str
    size_bytes: int
    head: bytes
    declared_mime: str | None = None

    def __post_init__(self) -> None:
        """Проводит быструю валидацию аргументов и нормализацию буфера.

        Raises:
            DomainValidationError: Если имя пустое, размер отрицательный
                или head не является bytes-подобным объектом.
        """
        if not self.original_filename.strip():
            raise DomainValidationError("original_filename не может быть пустым")

        if self.size_bytes < 0:
            raise DomainValidationError("size_bytes должен быть >= 0")

        if not isinstance(self.head, (bytes, bytearray, memoryview)):
            raise DomainValidationError("head должен быть bytes-подобным")

        if not isinstance(self.head, bytes):
            object.__setattr__(self, "head", bytes(self.head))


@dataclass(frozen=True, slots=True)
class TypeDetectionResult:
    """Результат детекции строгого типа документа.

    Attributes:
        type (DocumentType): Строгий тип.
        family (DocumentFamily): Семейство (производное от типа).
        ext (str | None): Нормализованное расширение без точки.
        mime (str | None): Нормализованный MIME.
        permission (Permission): Решение о допуске.
        confidence (float): Уверенность в диапазоне 0.0..1.0.
        warnings (tuple[str, ...]): Предупреждения, например конфликт MIME
            и сигнатуры.
    """

    type: DocumentType
    family: DocumentFamily
    ext: str | None
    mime: str | None
    permission: Permission
    confidence: float
    warnings: tuple[str, ...] = ()

    @property
    def is_allowed(self) -> bool:
        """Возвращает признак, что документ разрешён политикой.

        Returns:
            bool: True, если документ разрешён, иначе False.
        """
        return self.permission is Permission.ALLOWED

    @staticmethod
    def make(
        *,
        type_: DocumentType,
        ext: str | None,
        mime: str | None,
        confidence: float,
        warnings: tuple[str, ...] = (),
    ) -> TypeDetectionResult:
        """Создаёт результат, проверяя каноничность и вычисляя поля.

        На вход подаются уже нормализованные ext/mime от пограничного слоя.
        Внутри выполняется лёгкая проверка каноничности.

        Args:
            type_ (DocumentType): Строгий тип документа.
            ext (str | None): Нормализованное расширение без точки или None.
            mime (str | None): Нормализованный MIME или None.
            confidence (float): Уверенность в диапазоне 0.0..1.0.
            warnings (tuple[str, ...]): Сопутствующие предупреждения.

        Returns:
            TypeDetectionResult: Экземпляр результата детекции.

        Raises:
            DomainValidationError: Если нарушен диапазон confidence или ext/mime
                не каноничны.
        """
        if not (0.0 <= confidence <= 1.0):
            raise DomainValidationError("confidence должен быть в диапазоне 0.0..1.0")

        # Лёгкая проверка каноничности.
        if ext is not None and not _is_canonical_ext(ext):
            raise DomainValidationError("ext должен быть в нижнем регистре, без точки")
        if mime is not None and not _is_canonical_mime(mime):
            raise DomainValidationError("mime должен быть в формате тип/подтип, нижний")

        fam = family_of(type_)
        perm = permission_of(type_)

        return TypeDetectionResult(
            type=type_,
            family=fam,
            ext=ext,
            mime=mime,
            permission=perm,
            confidence=confidence,
            warnings=warnings,
        )


# Внутренние проверки каноничности
_EXT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")  # без точки, нижний регистр
_MIME_RE = re.compile(r"^[a-z0-9.+-]+/[a-z0-9.+-]+$")  # тип/подтип, нижний регистр


def _is_canonical_ext(ext: str) -> bool:
    return bool(_EXT_RE.fullmatch(ext))


def _is_canonical_mime(mime: str) -> bool:
    return bool(_MIME_RE.fullmatch(mime))
