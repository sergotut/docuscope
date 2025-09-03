"""Порт экстракции документов.

Определяет контракт для инфраструктурных адаптеров (DOCX/PDF/XLSX/OCR и др.).

Порт рассчитан на асинхронный поток элементов (stream), чтобы:
- не держать весь документ в памяти;
- давать сплиттеру ранний доступ к данным;
- уважать лимиты по страницам/времени.
"""

from __future__ import annotations

from typing import AsyncIterator, Protocol, runtime_checkable

from app.domain.model.diagnostics.health import DocumentExtractorHealthReport
from app.domain.model.documents import DocumentId
from app.domain.model.documents.extraction import (
    ExtractedItem,
    ExtractionOptions,
    ExtractorCapability,
)


@runtime_checkable
class DocumentExtractorPort(Protocol):
    """Абстрактный порт извлечения структурированного контента из документа.

    Определяет контракт для инфраструктурных адаптеров обработки различных
    форматов документов (DOCX, PDF, XLSX, изображения с OCR и др.).
    """

    async def is_healthy(self) -> bool:
        """Короткий health-check.

        Returns:
            bool: True, если экстрактор доступен.
        """
        ...

    async def health(self) -> DocumentExtractorHealthReport:
        """Подробный health-репорт.

        Returns:
            DocumentExtractorHealthReport: Подробная диагностика экстрактора.
        """
        ...

    def capabilities(self) -> ExtractorCapability:
        """Возвращает информацию о функциональных возможностях экстрактора.

        Описывает, какие виды метаданных может извлечь конкретная реализация:
        геометрию элементов, стили текста, структуру таблиц и т.п.

        Returns:
            ExtractorCapability: Описание возможностей экстрактора.
        """
        ...

    def supported_mime_types(self) -> tuple[str, ...]:
        """Возвращает список поддерживаемых MIME-типов.

        Определяет, какие типы документов может обработать экстрактор.
        Используется для маршрутизации документов к подходящему адаптеру.

        Returns:
            tuple[str, ...]: Кортеж MIME-типов.
        """
        ...

    def supported_extensions(self) -> tuple[str, ...]:
        """Возвращает список поддерживаемых расширений файлов.

        Дополняет supported_mime_types для случаев, когда MIME-тип
        неопределён или некорректен, но расширение файла известно.

        Returns:
            tuple[str, ...]: Кортеж расширений с точкой.
        """
        ...

    async def extract(
        self,
        *,
        doc_id: DocumentId,
        source_ref: str,
        options: ExtractionOptions | None = None,
    ) -> AsyncIterator[ExtractedItem]:
        """Выполняет потоковую экстракцию структурированных элементов документа.

        Асинхронно извлекает и возвращает элементы документа в порядке чтения.
        Поток может быть прерван при достижении лимитов или ошибках.

        Args:
            doc_id (DocumentId): Уникальный идентификатор документа в системе.
            source_ref (str): Ссылка на исходный объект, которую принимает
            инфраструктурный слой.
            options (ExtractionOptions | None): Конфигурация экстракции или None для
                значений по умолчанию.

        Yields:
            ExtractedItem: Структурированные элементы в порядке чтения документа.

        Raises:
            DomainValidationError: При некорректных параметрах (невалидный doc_id,
                пустой source_ref, неподдерживаемые опции).
            UnsupportedExtractionFormatError: При неподдерживаемом формате документа
                или отсутствии подходящего экстрактора.
            CorruptedDocumentError: При повреждённой структуре документа
                или нечитаемом содержимом.
            ExtractionTimeoutError: При превышении временных лимитов обработки.
            DocumentExtractionError: При других технических ошибках экстракции.
        """
        ...
