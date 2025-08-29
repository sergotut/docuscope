"""Репозиторий метаданных документов для PostgreSQL."""

from __future__ import annotations

from app.domain.model.collections import CollectionName
from app.domain.model.documents import DocumentMeta
from app.domain.model.shared import ObjectName
from app.domain.ports.relational_store import DocumentMetaRepositoryPort, RelConnection

__all__ = ["PostgresDocumentMetaRepository"]


class PostgresDocumentMetaRepository(DocumentMetaRepositoryPort):
    """Postgres-репозиторий метаданных документов."""

    def __init__(self, conn: RelConnection) -> None:
        """Инициализирует репозиторий.

        Args:
            conn (RelConnection): Активное соединение с БД.
        """
        self._c = conn

    async def add(self, meta: DocumentMeta) -> None:
        """Сохраняет или обновляет метаданные документа (upsert).

        Args:
            meta (DocumentMeta): Метаданные документа.
        """
        await self._c.execute(
            """
            insert into documents(
                id, title, collection, object_name, original_filename,
                mime, size_bytes, content_sha256, created_at
            ) values ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            on conflict (collection, id) do update set
                title = excluded.title,
                object_name = excluded.object_name,
                original_filename = excluded.original_filename,
                mime = excluded.mime,
                size_bytes = excluded.size_bytes,
                content_sha256 = excluded.content_sha256,
                created_at = excluded.created_at
            """,
            meta.id,
            meta.title,
            str(meta.collection),
            str(meta.object_name),
            meta.original_filename,
            meta.mime,
            meta.size_bytes,
            meta.content_sha256,
            meta.created_at,
        )

    async def list_by_collection(self, name: CollectionName) -> list[DocumentMeta]:
        """Возвращает все документы указанной коллекции.

        Args:
            name (CollectionName): Имя коллекции.

        Returns:
            list[DocumentMeta]: Список метаданных.
        """
        rows = await self._c.fetch(
            """
            select id, title, collection, object_name, original_filename,
                   mime, size_bytes, content_sha256, created_at
              from documents
             where collection = $1
             order by created_at asc
            """,
            str(name),
        )
        return [
            DocumentMeta(
                id=r["id"],
                title=r["title"],
                collection=CollectionName(r["collection"]),
                object_name=ObjectName(r["object_name"]),
                original_filename=r["original_filename"],
                mime=r["mime"],
                size_bytes=r["size_bytes"],
                content_sha256=r["content_sha256"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    async def delete_by_collection(self, name: CollectionName) -> None:
        """Удаляет все документы коллекции.

        Args:
            name (CollectionName): Имя коллекции.
        """
        await self._c.execute(
            "delete from documents where collection = $1",
            str(name),
        )
