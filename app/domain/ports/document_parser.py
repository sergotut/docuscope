"""Порт для парсеров документов (PDF, DOCX и др.)."""

from __future__ import annotations

from pathlib import Path
from collections.abc import IO
from typing import runtime_checkable, Protocol

from app.domain.nodes import DocumentNode


@runtime_checkable
class DocumentParserPort(Protocol):
    """Абстрактный порт парсера документа.

    Реализация должна принимать путь к файлу, строку или файловый поток,
    и возвращать результат в виде корневого узла DocumentNode.
    """

    def parse(self, src: str | Path | IO[bytes]) -> DocumentNode:
        """Парсит файл и строит дерево документа.

        Args:
            src (str | Path | IO[bytes]): Путь или поток к документу.

        Returns:
            DocumentNode: Корневой узел документа.
        """
        ...
