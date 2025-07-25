import structlog

logger = structlog.get_logger()


def seed():
    logger.info("seed_contracts")
    # placeholder
    print("Seeding demo contracts…")


# Скрипт для создания тестовых контрактов
if __name__ == "__main__":
    print("Скрипт seed_contracts.py: сгенерировано N тестовых контрактов")
