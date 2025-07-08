from celery import Celery
from app.core.settings import settings

celery_app = Celery(
    "docu_tasks",
    broker=f"redis://{settings.redis_host}:6379/0",
    backend=f"redis://{settings.redis_host}:6379/1",
)

celery_app.conf.task_routes = {
    "app.application.report_service.process_document_task": {"queue": "ingest"},
}
