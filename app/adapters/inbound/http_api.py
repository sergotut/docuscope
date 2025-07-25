import structlog
from fastapi import FastAPI, File, UploadFile

from app.infrastructure.task_queue import celery_app

app = FastAPI()
logger = structlog.get_logger()


@app.post("/api/upload/")
async def upload_doc(file: UploadFile = File(...)):
    file_bytes = await file.read()
    task = celery_app.send_task(
        "app.application.report_service.process_document_task",
        args=[file_bytes, file.filename, 0],
    )
    logger.bind(endpoint="upload_doc", filename=file.filename, user_id=0).info(
        "task_submitted", task_id=task.id
    )
    return {"task_id": task.id, "status": "processing"}
