"""
Конфигуратор логирования для «Документоскопа».

Работает с AppSettings (где секции: LoggingSettings, etc).
Автоматически подхватывает service_name, env, file/pretty-режим и уровни.
Поддерживает OpenTelemetry (если есть), suppression лишних логов, глобальный handler ошибок.
"""

import logging
import sys
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from app.core.settings import AppSettings

def service_metadata(settings):
    """Processor для добавления service и env в каждый лог."""
    def _processor(logger, method_name, event_dict):
        event_dict["service"] = getattr(settings, "service_name", "docuscope")
        event_dict["env"] = getattr(settings, "app_env", "prod")
        return event_dict
    return _processor

def init_logging(settings: "AppSettings") -> None:
    """
    Инициализирует логирование согласно settings.logging.

    Args:
        settings (AppSettings): Конфигурация приложения (с секцией logging).

    Returns:
        None
    """
    log_level = getattr(settings, "log_level", "INFO").upper()
    log_pretty = getattr(settings, "log_pretty", False)
    log_file = getattr(settings, "log_file", None)
    service_name = getattr(settings, "service_name", "docuscope")
    app_env = getattr(settings, "app_env", "prod")

    root_handlers = []
    # stdout handler (pretty для локала, JSON для prod)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(message)s"))
    root_handlers.append(stream_handler)

    # file handler (если нужен)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        root_handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        handlers=root_handlers,
        force=True,
    )

    # Подавляем шумные библиотеки
    for noisy in ("botocore", "boto3", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        service_metadata(settings),
        structlog.processors.format_exc_info,
    ]
    # OpenTelemetry trace_id (если есть)
    try:
        from structlog_opentelemetry.processors import add_trace_context
        processors.append(add_trace_context)
    except ImportError:
        pass

    if log_pretty:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level, logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )

    # Глобальный обработчик для uncaught exceptions
    def global_excepthook(exc_type, exc_value, exc_traceback):
        logging.getLogger("unhandled").error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
    sys.excepthook = global_excepthook
