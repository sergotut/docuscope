from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
        env_file = ".env"


settings = Settings()