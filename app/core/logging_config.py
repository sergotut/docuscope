import logging
import sys
from typing import Any

import structlog


def init_logging(settings: "Settings") -> None:  # noqa: ANN001
    """Инициализировать логирование всего приложения.

    • выводит лог-записи в stdout в формате JSON;
    • уровень задаётся через LOG_LEVEL / settings.log_level;
    • добавляет контекст, уровень и таймстамп;
    • скрывает лишний шум сторонних библиотек.
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
