"""Модели health-чеков и техинфы сервисов."""

from typing import TypedDict

__all__ = [
    "TokenizerHealthReport",
    "EmbedderHealthReport",
    "LLMHealthReport",
    "VectorStoreHealthReport",
    "RelationalDBHealthReport",
    "CacheHealthReport",
    "DocumentConverterHealthReport",
    "DocumentExtractorHealthReport",
]


class TokenizerHealthReport(TypedDict, total=False):
    """Расширенный отчёт токенайзера.

    Attributes:
        model (str): Имя/идентификатор модели.
        vocab_size (int): Размер словаря.
        encoding (str): Название кодировки/правил токенизации.
        version (str): Версия движка.
    """

    model: str
    vocab_size: int
    encoding: str
    version: str


class EmbedderHealthReport(TypedDict, total=False):
    """Расширенный отчёт эмбеддера.

    Attributes:
        model (str): Имя/идентификатор модели эмбеддингов.
        dim (int): Размерность эмбеддинга.
        framework (str): Фреймворк исполнения (например, torch).
        device (str): Устройство исполнения (cpu, cuda, mps).
        version (str): Версия движка/библиотеки.
    """

    model: str
    dim: int
    framework: str
    device: str
    version: str


class LLMHealthReport(TypedDict, total=False):
    """Расширенный отчёт LLM.

    Attributes:
        model (str): Имя/идентификатор LLM.
        provider (str): Провайдер/хостинг (например, openai, local).
        context_window (int): Максимальный контекст в токенах.
        max_output_tokens (int): Лимит вывода в токенах.
        version (str): Версия API/модели.
    """

    model: str
    provider: str
    context_window: int
    max_output_tokens: int
    version: str


class VectorStoreHealthReport(TypedDict, total=False):
    """Расширенный отчёт векторного хранилища (например, Qdrant).

    Attributes:
        engine (str): Название движка.
        version (str): Версия сервиса.
        distance (str): Метрика расстояния (cosine, dot, euclid).
        collections (int): Количество коллекций.
        status (str): Текущий статус/режим работы.
    """

    engine: str
    version: str
    distance: str
    collections: int
    status: str


class RelationalDBHealthReport(TypedDict, total=False):
    """Отчёт о состоянии реляционного хранилища.

    Все поля необязательны для сохранения обратной совместимости.

    Attributes:
        engine (str): Название СУБД.
        version (str): Версия сервера БД.
        dsn (str): DSN или краткая строка подключения.
        database (str): Имя базы данных.
        status (str): Текущий статус работы.
        pool_min (int): Минимальный размер пула подключений.
        pool_max (int): Максимальный размер пула подключений.
        pool_in_use (int): Текущие занятые подключения.
        latency_ms (float): Оценка сетевой/SQL-задержки в миллисекундах.
        role (str): Роль экземпляра (primary или replica).
        readonly (bool): Признак режима только для чтения.
        max_connections (int): Лимит подключений сервера.
        num_backends (int): Активные подключения к текущей БД.
        xact_commit (int): Счётчик коммитов транзакций.
        xact_rollback (int): Счётчик откатов транзакций.
        buffers_cache_hit_ratio (float): Доля попаданий в кеш 0..1.
        uptime_seconds (int): Время работы сервера в секундах.
    """

    engine: str
    version: str
    dsn: str
    database: str
    status: str
    pool_min: int
    pool_max: int
    pool_in_use: int
    latency_ms: float
    role: str
    readonly: bool
    max_connections: int
    num_backends: int
    xact_commit: int
    xact_rollback: int
    buffers_cache_hit_ratio: float
    uptime_seconds: int


class CacheHealthReport(TypedDict, total=False):
    """Отчёт о состоянии кэширующего движка.

    Attributes:
        engine (str): Название движка (например, redis).
        version (str): Версия сервера.
        dsn (str): DSN или краткая строка подключения.
        role (str): Роль экземпляра (master/replica).
        status (str): Текущий статус работы.
        latency_ms (float): Оценка сетевой задержки в миллисекундах.
        db (int): Индекс выбранной базы (если применимо).
        uptime_seconds (int): Время работы сервера в секундах.
        used_memory_bytes (int): Используемая память в байтах.
        connected_clients (int): Число подключённых клиентов.
        total_commands_processed (int): Обработано команд всего.
        keyspace_keys (int): Количество ключей.
        keyspace_expires (int): Количество ключей с TTL.
        hit_ratio (float): Доля попаданий в кэш 0..1.
    """

    engine: str
    version: str
    dsn: str
    role: str
    status: str
    latency_ms: float
    db: int
    uptime_seconds: int
    used_memory_bytes: int
    connected_clients: int
    total_commands_processed: int
    keyspace_keys: int
    keyspace_expires: int
    hit_ratio: float


class DocumentConverterHealthReport(TypedDict, total=False):
    """Расширенный отчёт конвертера документов.

    Attributes:
        engine (str): Название движка конвертации (например, libreoffice, pandoc).
        version (str): Версия конвертера или API.
        status (str): Текущий статус работы конвертера.
        supported_formats (list[str]): Список поддерживаемых форматов конвертации.
        concurrent_conversions (int): Количество одновременных конвертаций.
        max_concurrent_conversions (int): Максимальное количество параллельных операций.
        total_conversions (int): Общее количество выполненных конвертаций.
        successful_conversions (int): Количество успешных конвертаций.
        failed_conversions (int): Количество неудачных конвертаций.
        average_conversion_time_ms (float): Среднее время конвертации в миллисекундах.
        queue_size (int): Размер очереди ожидающих конвертации документов.
        temp_dir_size_bytes (int): Размер временной директории в байтах.
        uptime_seconds (int): Время работы сервиса в секундах.
        last_conversion_timestamp (int): Время последней конвертации (Unix timestamp).
    """

    engine: str
    version: str
    status: str
    supported_formats: list[str]
    concurrent_conversions: int
    max_concurrent_conversions: int
    total_conversions: int
    successful_conversions: int
    failed_conversions: int
    average_conversion_time_ms: float
    queue_size: int
    temp_dir_size_bytes: int
    uptime_seconds: int
    last_conversion_timestamp: int


class DocumentExtractorHealthReport(TypedDict, total=False):
    """Отчёт о состоянии экстрактора документов.

    Attributes:
        engine (str): Название движка экстракции (например, docx, pdfminer, openpyxl).
        version (str): Версия движка или библиотеки.
        status (str): Текущий статус работы.
        queue_size (int): Размер очереди задач экстракции.
        uptime_seconds (int): Время работы сервиса в секундах.
    """

    engine: str
    version: str
    status: str
    queue_size: int
    uptime_seconds: int
