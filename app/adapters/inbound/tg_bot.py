import logging, asyncio
from aiogram import Bot, Dispatcher, types
from app.core.settings import settings
from app.infrastructure.task_queue import celery_app

bot = Bot(token=settings.telegram_token)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    if message.document:
        file = await message.bot.get_file(message.document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        task = celery_app.send_task(
            "app.application.report_service.process_document_task",
            args=[file_bytes.read(), message.document.file_name, message.from_user.id]
        )
        await message.reply("Документ принят, анализ идёт... Ждите отчёт!")
    else:
        await message.reply("Пришли файл PDF/DOCX для анализа!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
