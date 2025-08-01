"""Главный DI-контейнер приложения.

Работает с новой структурой settings и structlog.
"""

import time

import structlog
from dependency_injector import containers, providers

from app.core.settings import settings

from .di_mappings import EMBEDDERS, LLMS, OCRS, STORAGES, VSTORES

logger = structlog.get_logger(__name__)


def _selector(
    attr_name: str, mapping: dict[str, type], category: str
) -> providers.Provider:
    """Создаёт DI Selector с логгированием и защитой от ошибок.

    Args:
        attr_name (str): Имя параметра в конфиге (например, "embedder").
        mapping (dict[str, type]): Сопоставление ключа и класса.
        category (str): Название категории (для логов).

    Returns:
        providers.Provider: Selector-провайдер с логированием.
    """
    def get_key():
        """Извлекает ключ из соответствующего namespace в settings.

        ai секция: embedder, llm_provider, vector_backend
        storage секция: storage_backend
        ocr секция: ocr_provider
        """
        val = (
            getattr(settings.ai, attr_name, None)
            or getattr(settings.minio, attr_name, None)
            or getattr(settings, attr_name, "null")
        )
        if val not in mapping:
            logger.warning(
                "DI: Неизвестный ключ для %s, используется NullObject",
                category,
                key=val,
            )
            return "null"
        return val

    class LoggingProvider(providers.Singleton):
        """Провайдер, логирующий время создания объекта."""
        
        def __call__(self, *args, **kwargs):
            """Создаёт и возвращает экземпляр провайдера с логированием.

            Args:
                *args: Позиционные аргументы, переданные в класс.
                **kwargs: Именованные аргументы, переданные в класс.
            Returns:
                Any: Экземпляр класса, обёрнутый в логирование.
            """
            start = time.monotonic()
            try:
                obj = super().__call__(*args, **kwargs)
                logger.info(
                    "DI: %s(%s) создан",
                    category,
                    key=get_key(),
                    time_ms=(time.monotonic() - start) * 1000,
                )
                return obj
            except Exception as ex:
                logger.exception(
                    "DI: Ошибка создания %s(%s): %s", category, get_key(), ex
                )
                raise

    return providers.Selector(
        providers.Callable(get_key),
        **{key: LoggingProvider(cls) for key, cls in mapping.items()},
    )


class Container(containers.DeclarativeContainer):
    """Главный DI-контейнер приложения.

    Использует DI-обёртки и новую структуру настроек.
    """

    wiring_config = containers.WiringConfiguration(packages=["app"])

    embedding = _selector("embedder", EMBEDDERS, "embedder")
    llm = _selector("llm_provider", LLMS, "llm")
    vector_store = _selector("vector_backend", VSTORES, "vector_store")
    ocr = _selector("ocr_provider", OCRS, "ocr")
    storage = _selector("storage_backend", STORAGES, "storage")

    def health(self) -> dict:
        """Проверяет здоровье всех зарегистрированных компонентов.

        Returns:
            dict: Статус по каждому компоненту (True/False).
        """
        result = {}
        for name, prov in [
            ("embedding", self.embedding),
            ("llm", self.llm),
            ("vector_store", self.vector_store),
            ("ocr", self.ocr),
            ("storage", self.storage),
        ]:
            try:
                obj = prov()
                healthy = getattr(obj, "is_healthy", lambda: False)()
            except Exception as ex:
                logger.exception("DI: Ошибка health для %s: %s", name, ex)
                healthy = False
            result[name] = healthy
        return result
