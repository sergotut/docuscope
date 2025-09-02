"""DTO уровня application для экстракторов документов.

Содержит унифицированные DTO чанков и вспомогательные модели.
Используется для транспорта данных между адаптерами, нормализацией,
сплиттером и эмбеддером.
"""

from __future__ import annotations

from .enums import (
    ChunkKind,
    ListStyle,
    ScriptPosition,
    ColumnType,
)
from .common import (
    BBoxDTO,
    FontStyleDTO,
    LinkDTO,
    RichTextSpanDTO,
    TableCellRefDTO,
    TableContextDTO,
    SectionPathDTO,
    ProvenanceDTO,
)
from .positions import (
    DocxPositionDTO,
    PdfPositionDTO,
    XlsxCellDTO,
)
from .table import (
    TableDTO,
    TableColumnDTO,
    TableRowDTO,
    TableCellDTO,
)
from .chunk import (
    BaseChunkDTO,
    DocxChunkDTO,
    PdfTextChunkDTO,
    XlsxChunkDTO,
    AnyChunkDTO,
)

__all__ = [
    # Перечисления (enum)
    "ChunkKind",
    "ListStyle",
    "ScriptPosition",
    "ColumnType",
    # Вспомогательные модели
    "BBoxDTO",
    "FontStyleDTO",
    "LinkDTO",
    "RichTextSpanDTO",
    "TableCellRefDTO",
    "TableContextDTO",
    "SectionPathDTO",
    "ProvenanceDTO",
    # Позиционные модели
    "DocxPositionDTO",
    "PdfPositionDTO",
    "XlsxCellDTO",
    # Табличные модели
    "TableDTO",
    "TableColumnDTO",
    "TableRowDTO",
    "TableCellDTO",
    # Модели чанков
    "BaseChunkDTO",
    "DocxChunkDTO",
    "PdfTextChunkDTO",
    "XlsxChunkDTO",
    "AnyChunkDTO",
]
