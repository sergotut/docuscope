"""
Модуль конфигурации приложения «Документоскоп».

Содержит описание класса Settings для централизованного хранения и валидации
конфигурационных параметров, необходимых для работы сервиса. Использует
Pydantic BaseSettings для автоматического чтения переменных из файла .env
или окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс конфигурации приложения.

    Описывает все параметры, которые должны быть заданы через переменные окружения
    или в файле .env. Используется для инициализации настроек всех ключевых сервисов.

    Attributes:
        app_env (str): Окружение приложения (prod/dev).
        postgres_dsn (str): DSN-строка подключения к PostgreSQL.
        minio_endpoint (str): Адрес MinIO для хранения файлов.
        minio_access_key (str): Ключ доступа к MinIO.
        minio_secret_key (str): Секретный ключ MinIO.
        embedder (str): Модель эмбеддинга (например, "yagpt").
        vector_backend (str): Бэкенд для хранения векторов (например, "qdrant").
        llm_provider (str): Провайдер LLM (например, "yagpt").
        doc_ttl_min (int): Время жизни документов (TTL) в минутах.
        free_limit (int): Лимит бесплатных обработок документов.
        team_limit (int): Лимит для командного тарифа.
        ygpt_key (str): Ключ API YandexGPT.
        telegram_token (str): Токен Telegram-бота.
        webhook_path (str): Путь для Telegram Webhook.
        redis_host (str): Хост для Redis.
        celery_broker_url (str): URL брокера задач Celery.
        celery_result_backend (str): Бэкенд хранения результатов Celery.
        log_level (str): Уровень логирования приложения.
    """
    
    app_env: str = "prod"
    postgres_dsn: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    embedder: str = "yagpt"
    vector_backend: str = "qdrant"
    llm_provider: str = "yagpt"
    doc_ttl_min: int = 60
    free_limit: int = 10
    team_limit: int = 100
    ygpt_key: str = ""
    telegram_token: str = ""
    webhook_path: str = "/webhook/abcdef"
    redis_host: str = "redis"
    celery_broker_url: str
    celery_result_backend: str

    # Настройка логирования
    log_level: str = "INFO"  # DEBUG / INFO / WARNING / ERROR / CRITICAL

    class Config:
        """
        Конфигурация Pydantic BaseSettings.

        Указывает, что переменные окружения могут браться из файла .env.
        """
        env_file = ".env"


settings = Settings()
