"""
Конфигурация логирования для сервиса «Документоскоп».

Данный модуль отвечает за настройку форматирования и уровней логирования
для всего приложения. Логирование включает вывод в stdout с уровнем логов,
форматированием времени и поддержкой цветного вывода для удобства при
отладке и мониторинге. Настройки зависят от конфигурации среды.
"""

import logging
import sys
from typing import Any, TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from app.core.settings import Settings


def init_logging(settings: "Settings") -> None:  # noqa: ANN001
    """
    Инициализирует логирование для всего приложения.

    Настраивает базовый логгер, подавляет лишний шум от сторонних библиотек
    и подключает structlog для вывода логов в формате JSON.

    Args:
        settings (Settings): Экземпляр класса Settings с конфигурацией уровня логирования.
    
    Returns:
        None: Функция не возвращает значения.

    Пример:
        >>> from app.core.settings import Settings
        >>> settings = Settings()
        >>> init_logging(settings)
    """
    log_level = settings.log_level.upper()

    # Базовая настройка stdlib-logging
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(message)s",  # финальный JSON формируется в structlog
        stream=sys.stdout,
    )

    # Подавляем лишние логи популярных библиотек
    for noisy in ("botocore", "boto3", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Подключаем structlog
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=shared_processors + [structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level, logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )
