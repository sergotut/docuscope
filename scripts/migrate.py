import structlog
logger = structlog.get_logger()

def migrate():
    logger.info("run_migrations")
    # placeholder для миграция Alembic
    print("Running DB migrations…")

# Здесь можно запускать alembic или другие миграции
if __name__ == "__main__":
    migrate()
    print("Скрипт migrate.py: миграции БД применены")
