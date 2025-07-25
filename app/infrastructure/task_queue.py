import structlog
from celery import Celery

from app.core.settings import settings

logger = structlog.get_logger()

# 1. создаём экземпляр Celery
celery_app = Celery(
    "docu_tasks",
    broker=f"redis://{settings.redis_host}:6379/0",
    backend=f"redis://{settings.redis_host}:6379/1",
)

# 2. регистрируем свои задачи
#    (импорт → декоратор .task сработает → задача попадёт в celery_app)
from app.application.report_service import process_document_task  # noqa: F401

# 3. опциональный роут / очередь
celery_app.conf.task_routes = {
    "app.application.report_service.process_document_task": {"queue": "ingest"},
}

logger.info(
    "celery_configured",
    broker=celery_app.conf.broker_url,
    backend=celery_app.conf.result_backend,
)
