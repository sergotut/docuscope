"""
Telegram-бот для сервиса 'Документоскоп': обработка сообщений, загрузка документов и отправка статусов.
"""

import asyncio

import structlog
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.adapters.inbound.task_result_tracker import task_registry, track_results
from app.core.logging_config import init_logging
from app.core.settings import settings
from app.infrastructure.task_queue import celery_app

init_logging(settings)
logger = structlog.get_logger()

bot = Bot(
    token=settings.telegram_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    """
    Обрабатывает входящие сообщения пользователей Telegram-бота.

    Если пользователь отправляет документ — инициирует его обработку,
    сохраняет task_id для отслеживания, отправляет ответ пользователю.
    В случае ошибки отправляет соответствующее уведомление.

    Args:
        message (types.Message): Объект сообщения Telegram от пользователя.
    """
    bound = logger.bind(user_id=message.from_user.id)
    if message.document:
        try:
            file = await bot.get_file(message.document.file_id)
            file_bytes = await bot.download_file(file.file_path)

            bound.info("doc_received", filename=message.document.file_name)

            task = celery_app.send_task(
                "app.application.report_service.process_document_task",
                args=[
                    file_bytes.read(),
                    message.document.file_name,
                    message.from_user.id,
                ],
            )
            task_registry[task.id] = message.chat.id

            bound.info("task_submitted", task_id=task.id)
            await message.reply("Документ принят, анализ начался... ⏳")
        except Exception as e:
            bound.error("file_processing_error", error=str(e))
            await message.reply("Произошла ошибка при обработке файла 😥")
    else:
        bound.info("non_document_message")
        await message.reply("Пришли файл PDF или DOCX для анализа 📄")


async def main():
    """
    Основная точка входа для запуска Telegram-бота.

    Инициализирует задачу отслеживания статусов Celery и запускает polling для обработки сообщений.
    """
    logger.info("bot_started")
    asyncio.create_task(track_results(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    """
    Точка входа при запуске файла как скрипта.

    Запускает основной цикл бота через asyncio.
    """
    asyncio.run(main())
