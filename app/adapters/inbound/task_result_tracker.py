import asyncio
from celery.result import AsyncResult
from aiogram import Bot
import structlog

from app.core.settings import settings
from app.infrastructure.task_queue import celery_app

logger = structlog.get_logger()

# Храним ID задач, которые нужно отслеживать
task_registry = {}  # task_id -> chat_id

async def track_results(bot: Bot):
    while True:
        await asyncio.sleep(2)
        finished = []

        for task_id, chat_id in task_registry.items():
            result = AsyncResult(task_id, app=celery_app)
            if result.ready():
                try:
                    output = result.get()
                    summary = output["summary"]
                    await bot.send_message(chat_id, f"📄 Готово! Результат:\n\n{summary}")
                    logger.info("result_sent", user_id=chat_id, task_id=task_id)
                except Exception as e:
                    await bot.send_message(chat_id, "⚠️ Произошла ошибка при обработке файла.")
                    logger.error("result_error", error=str(e), task_id=task_id)
                finished.append(task_id)

        for tid in finished:
            task_registry.pop(tid, None)
