"""
Точка входа для запуска HTTP API сервиса Документоскоп.

Модуль инициализирует логирование и запускает FastAPI-приложение через Uvicorn.
Используется только для dev/prod-развертывания как скрипт.

Все параметры сервера (host, port и пр.) берутся из ENV или конфигурации.
"""

import uvicorn

from app.adapters.inbound.http_api import app
from app.core.logging_config import init_logging
from app.core.settings import settings

# Инициализируем логирование до старта приложения,
# чтобы все ранние сообщения были структурированными.
init_logging(settings)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104: Необходим для работы в контейнере/облаке
        port=8000,
        log_config=None,  # форматирование делает structlog
        access_log=False,  # отключаем стандартный access-лог Uvicorn
    )
