from fastapi import FastAPI, UploadFile, File, BackgroundTasks

from app.infrastructure.task_queue import celery_app

app = FastAPI()

@app.post("/api/upload/")
async def upload_doc(file: UploadFile = File(...)):
    file_bytes = await file.read()
    task = celery_app.send_task(
        "app.application.report_service.process_document_task",
        args=[file_bytes, file.filename, 0]
    )
    return {"task_id": task.id, "status": "processing"}
