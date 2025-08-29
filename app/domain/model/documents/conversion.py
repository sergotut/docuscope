"""Доменные модели для конвертации документов между форматами.

Содержит value objects и enums для операций конвертации документов
из устаревших форматов в современные (doc->docx, xls->xlsx).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from app.domain.exceptions import DomainValidationError
from app.domain.model.documents.document import DocumentId
from app.domain.model.documents.types import DocumentType
from app.domain.shared.codes import WarningCode

__all__ = [
    "ConversionStatus",
    "ConversionRequest",
    "ConversionResult",
    "SUPPORTED_CONVERSIONS",
    "is_conversion_supported",
]


# Поддерживаемые пары конвертации (исходный_тип, целевой_тип).
SUPPORTED_CONVERSIONS: Final[frozenset[tuple[DocumentType, DocumentType]]] = frozenset(
    {
        (DocumentType.WORD_DOC, DocumentType.WORD_DOCX),
        (DocumentType.EXCEL_XLS, DocumentType.EXCEL_XLSX),
    }
)


class ConversionStatus(str, Enum):
    """Статус операции конвертации документа.

    Attributes:
        SUCCESS: Конвертация выполнена успешно без потерь.
        SUCCESS_WITH_WARNINGS: Конвертация выполнена с предупреждениями
            о возможной потере качества или неподдерживаемых функциях.
        FAILED: Конвертация не удалась из-за технических ошибок
            или несовместимости форматов.
    """

    SUCCESS = "success"
    SUCCESS_WITH_WARNINGS = "success_with_warnings"
    FAILED = "failed"


def is_conversion_supported(
    from_type: DocumentType,
    to_type: DocumentType,
) -> bool:
    """Проверяет поддержку конвертации между указанными типами.

    Args:
        from_type (DocumentType): Исходный тип документа.
        to_type (DocumentType): Целевой тип документа.

    Returns:
        bool: True, если конвертация поддерживается, иначе False.
    """
    return (from_type, to_type) in SUPPORTED_CONVERSIONS


@dataclass(frozen=True, slots=True)
class ConversionRequest:
    """Запрос на конвертацию документа в другой формат.

    Attributes:
        document_id (DocumentId): Идентификатор исходного документа.
        from_type (DocumentType): Исходный тип документа.
        to_type (DocumentType): Целевой тип документа.
        source_data (bytes): Исходные данные документа в бинарном виде.
        preserve_metadata (bool): Сохранять ли метаданные при конвертации.
    """

    document_id: DocumentId
    from_type: DocumentType
    to_type: DocumentType
    source_data: bytes
    preserve_metadata: bool = True

    def __post_init__(self) -> None:
        """Валидирует корректность запроса на конвертацию.

        Raises:
            DomainValidationError: Если типы конвертации не поддерживаются,
                исходные данные пусты, или from_type равен to_type.
        """
        if self.from_type == self.to_type:
            raise DomainValidationError(
                f"Исходный и целевой типы не могут совпадать: {self.from_type}"
            )

        if not is_conversion_supported(self.from_type, self.to_type):
            raise DomainValidationError(
                f"Конвертация {self.from_type} -> {self.to_type} не поддерживается"
            )

        if not self.source_data:
            raise DomainValidationError("source_data не может быть пустым")

    @property
    def is_word_conversion(self) -> bool:
        """Возвращает признак конвертации документов Word.

        Returns:
            bool: True, если это конвертация Word-документа, иначе False.
        """
        return (self.from_type, self.to_type) == (
            DocumentType.WORD_DOC,
            DocumentType.WORD_DOCX,
        )

    @property
    def is_excel_conversion(self) -> bool:
        """Возвращает признак конвертации документов Excel.

        Returns:
            bool: True, если это конвертация Excel-документа, иначе False.
        """
        return (self.from_type, self.to_type) == (
            DocumentType.EXCEL_XLS,
            DocumentType.EXCEL_XLSX,
        )


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Результат операции конвертации документа.

    Attributes:
        document_id (DocumentId): Идентификатор исходного документа.
        status (ConversionStatus): Статус операции конвертации.
        converted_data (bytes | None): Данные сконвертированного документа
            в случае успеха, иначе None.
        target_type (DocumentType): Целевой тип документа.
        warnings (tuple[WarningCode, ...]): Предупреждения о потере качества
            или неподдерживаемых функциях.
        error_message (str | None): Сообщение об ошибке в случае неудачи.
        size_bytes (int): Размер результирующего документа в байтах.
    """

    document_id: DocumentId
    status: ConversionStatus
    converted_data: bytes | None
    target_type: DocumentType
    warnings: tuple[WarningCode, ...] = ()
    error_message: str | None = None
    size_bytes: int = 0

    def __post_init__(self) -> None:
        """Валидирует корректность результата конвертации.

        Raises:
            DomainValidationError: Если статус SUCCESS, но данные отсутствуют,
                или статус FAILED, но данные присутствуют, или size_bytes
                отрицательный.
        """
        if self.status == ConversionStatus.SUCCESS and not self.converted_data:
            raise DomainValidationError(
                "При статусе SUCCESS converted_data не может быть None"
            )

        if (
            self.status == ConversionStatus.SUCCESS_WITH_WARNINGS
            and not self.converted_data
        ):
            raise DomainValidationError(
                "При статусе SUCCESS_WITH_WARNINGS converted_data не может быть None"
            )

        if self.status == ConversionStatus.FAILED and self.converted_data:
            raise DomainValidationError(
                "При статусе FAILED converted_data должен быть None"
            )

        if self.size_bytes < 0:
            raise DomainValidationError("size_bytes должен быть >= 0")

        # Проверяем соответствие размера данных и size_bytes
        if self.converted_data and self.size_bytes != len(self.converted_data):
            raise DomainValidationError(
                f"size_bytes ({self.size_bytes}) не соответствует "
                f"длине converted_data ({len(self.converted_data)})"
            )

    @property
    def is_successful(self) -> bool:
        """Возвращает признак успешной конвертации.

        Returns:
            bool: True, если конвертация прошла успешно (с предупреждениями
                или без), иначе False.
        """
        return self.status in (
            ConversionStatus.SUCCESS,
            ConversionStatus.SUCCESS_WITH_WARNINGS,
        )

    @property
    def has_warnings(self) -> bool:
        """Возвращает признак наличия предупреждений.

        Returns:
            bool: True, если есть предупреждения, иначе False.
        """
        return bool(self.warnings)

    @staticmethod
    def success(
        *,
        document_id: DocumentId,
        converted_data: bytes,
        target_type: DocumentType,
        warnings: tuple[WarningCode, ...] = (),
    ) -> ConversionResult:
        """Создаёт результат успешной конвертации.

        Args:
            document_id (DocumentId): Идентификатор документа.
            converted_data (bytes): Данные сконвертированного документа.
            target_type (DocumentType): Целевой тип документа.
            warnings (tuple[WarningCode, ...]): Предупреждения конвертации.

        Returns:
            ConversionResult: Результат успешной конвертации.
        """
        status = (
            ConversionStatus.SUCCESS_WITH_WARNINGS
            if warnings
            else ConversionStatus.SUCCESS
        )

        return ConversionResult(
            document_id=document_id,
            status=status,
            converted_data=converted_data,
            target_type=target_type,
            warnings=warnings,
            size_bytes=len(converted_data),
        )

    @staticmethod
    def failure(
        *,
        document_id: DocumentId,
        target_type: DocumentType,
        error_message: str,
        warnings: tuple[WarningCode, ...] = (),
    ) -> ConversionResult:
        """Создаёт результат неудачной конвертации.

        Args:
            document_id (DocumentId): Идентификатор документа.
            target_type (DocumentType): Целевой тип документа.
            error_message (str): Сообщение об ошибке.
            warnings (tuple[WarningCode, ...]): Предупреждения конвертации.

        Returns:
            ConversionResult: Результат неудачной конвертации.
        """
        return ConversionResult(
            document_id=document_id,
            status=ConversionStatus.FAILED,
            converted_data=None,
            target_type=target_type,
            warnings=warnings,
            error_message=error_message,
        )
