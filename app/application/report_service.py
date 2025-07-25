import structlog

from app.adapters.outbound.embedding_yagpt import YandexGPTEmbedding
from app.adapters.outbound.llm_yagpt import YaGPTLLM
from app.adapters.outbound.ocr_paddle import PaddleOCRAdapter
from app.adapters.outbound.vectordb_qdrant import QdrantVectorStore
from app.infrastructure.task_queue import celery_app

logger = structlog.get_logger()


@celery_app.task(name="app.application.report_service.process_document_task")
def process_document_task(
    file_bytes: bytes, filename: str, user_id: int
):  # noqa: ANN001
    """Полный пайплайн:

    1. OCR (если требуется);
    2. разбиение текста на чанки;
    3. генерация эмбеддингов;
    4. сохранение в Qdrant;
    5. анализ LLM;
    6. возврат структуры отчёта (демо-режим).
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

        # 2. Разбиваем на чанки длиной 500 символов
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
