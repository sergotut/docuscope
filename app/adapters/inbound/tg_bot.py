"""
Telegram-бот для сервиса 'Документоскоп'.

Реализует прием документов от пользователя, запуск анализа через Celery,
и отправку статуса/результата пользователю в Telegram. Поддерживает трекинг задач.
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
logger = structlog.get_logger(__name__)

bot = Bot(
    token=settings.telegram_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    """
    Обрабатывает входящее сообщение пользователя Telegram-бота.

    Если сообщение содержит документ, инициирует его обработку через Celery и
    регистрирует задачу для последующего отслеживания статуса.
    В случае ошибки отправляет уведомление пользователю.

    Args:
        message (types.Message): Сообщение пользователя Telegram.
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

    Запускает задачу трекинга Celery и polling dispatcher для обработки
    входящих сообщений.

    Returns:
        None
    """
    logger.info("bot_started")
    asyncio.create_task(track_results(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    """
    Запускает основной цикл Telegram-бота при запуске файла как скрипта.
    """
    asyncio.run(main())
