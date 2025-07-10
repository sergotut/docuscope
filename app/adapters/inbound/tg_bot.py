import asyncio
import structlog
from aiogram import Bot, Dispatcher, types

from app.core.settings import settings
from app.core.logging_config import init_logging
from app.infrastructure.task_queue import celery_app

init_logging(settings)
logger = structlog.get_logger()

bot = Bot(token=settings.telegram_token)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    bound = logger.bind(user_id=message.from_user.id)
    if message.document:
        file = await message.bot.get_file(message.document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        bound.info("doc_received", filename=message.document.file_name)
        task = celery_app.send_task(
            "app.application.report_service.process_document_task",
            args=[file_bytes.read(), message.document.file_name, message.from_user.id],
        )
        bound.info("task_submitted", task_id=task.id)
        await message.reply("Документ принят, анализ идёт... Ждите отчёт!")
    else:
        bound.info("non_document_message")
        await message.reply("Пришли файл PDF/DOCX для анализа!")

async def main():
    logger.info("bot_started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
