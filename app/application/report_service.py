from app.infrastructure.task_queue import celery_app
from app.adapters.outbound.ocr_paddle import PaddleOCRAdapter
from app.adapters.outbound.embedding_yagpt import YandexGPTEmbedding
from app.adapters.outbound.vectordb_qdrant import QdrantVectorStore
from app.adapters.outbound.llm_yagpt import YaGPTLLM

@celery_app.task(name="app.application.report_service.process_document_task")
def process_document_task(file_bytes, filename, user_id):
    # 1. OCR (если нужно)
    text = PaddleOCRAdapter().ocr(file_bytes)
    # 2. Chunk (порежем на строки, как пример)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    # 3. Embedding
    vectors = YandexGPTEmbedding(key="demo").embed(chunks)
    # 4. Qdrant upsert
    QdrantVectorStore(url="http://qdrant:6333").upsert(vectors, [{"chunk": c} for c in chunks])
    # 5. LLM-анализ (мок)
    summary = YaGPTLLM(key="demo").generate("Дай сводку договора", text)
    # 6. Вернуть отчет (в реале — сохранить в БД)
    return {"summary": summary}
