import structlog

logger = structlog.get_logger()

class BillingService:
    def __init__(self):
        pass

    def check_limits(self, user_id: int) -> bool:
        # Мок: проверка лимитов пользователя
        allowed = True
        logger.debug("check_limits", user_id=user_id, allowed=allowed)
        return allowed
