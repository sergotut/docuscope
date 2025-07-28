"""Модуль сервиса генерации отчётов по загруженным документам для проекта.

Реализует асинхронный пайплайн Celery для анализа документов:
- OCR (при необходимости),
- разбиение на чанки,
- генерация эмбеддингов,
- сохранение в Qdrant,
- вызов LLM для анализа содержания,
- возврат или сохранение отчёта.

Используется как основной обработчик документов при загрузке через Telegram-бота
или API.
"""

import structlog

from app.adapters.outbound.embedding.yagpt import YandexGPTEmbedding
from app.adapters.outbound.llm.yagpt import YaGPTLLM
from app.adapters.outbound.ocr.paddle import PaddleOCRAdapter
from app.adapters.outbound.vector.qdrant import QdrantVectorStore
from app.infrastructure.task_queue import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.application.report_service.process_document_task")
def process_document_task(file_bytes: bytes, filename: str, user_id: int):
    """Полный пайплайн обработки документа для анализа.

    1. OCR (если требуется);
    2. Разбиение текста на чанки;
    3. Генерация эмбеддингов;
    4. Сохранение в Qdrant;
    5. Анализ с помощью LLM;
    6. Возврат структуры отчёта (демо-режим).

    Args:
        file_bytes (bytes): Сырые байты загруженного файла (PDF, DOCX, фото).
        filename (str): Имя файла документа.
        user_id (int): Идентификатор пользователя, загрузившего файл.

    Returns:
        dict: Словарь с краткой сводкой по документу (в продуктиве — запись в БД).

    Raises:
        Exception: Любая ошибка в процессе обработки будет залогирована и проброшена.
    """
    task_logger = logger.bind(
        celery_task="process_document",
        task_id=process_document_task.request.id,
        user_id=user_id,
        filename=filename,
    )
    task_logger.info("start_processing")

    try:
        # 1. OCR
        text = PaddleOCRAdapter().ocr(file_bytes)
        task_logger.debug("ocr_complete", text_len=len(text))

        chunks = [text[i : i + 500] for i in range(0, len(text), 500)]
        task_logger.debug("split_into_chunks", chunks=len(chunks))

        # 3. Эмбеддинги
        vectors = YandexGPTEmbedding(key="demo").embed(chunks)
        task_logger.debug("embedding_generated", vectors=len(vectors))

        # 4. Сохраняем в Qdrant
        QdrantVectorStore(url="http://qdrant:6333").upsert(
            vectors, [{"chunk": c} for c in chunks]
        )
        task_logger.info("vectors_upserted", count=len(vectors))

        # 5. Анализ LLM
        summary = YaGPTLLM(key="demo").generate("Дай сводку договора", text)
        task_logger.info("llm_summary_ready")

        # 6. Возвращаем (в продуктиве сохраняем в БД)
        return {"summary": summary}

    except Exception as exc:  # noqa: BLE001
        task_logger.exception("processing_failed", error=str(exc))
        raise
