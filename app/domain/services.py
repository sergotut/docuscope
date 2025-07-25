import structlog

logger = structlog.get_logger()


class ContractExtractor:
    def __init__(self):
        pass

    def extract_main_terms(self, text: str) -> dict:
        logger.debug("extract_main_terms", text_len=len(text))  # логгирование
        # Мок: извлечение сторон, сроков, штрафов и условий
        return {
            "parties": "ООО Альфа — ООО Бета",
            "duration": "01.07.2025 – 30.06.2026",
            "price": "12 000 000 ₽",
            "penalty": "0,1 % в день",
            "risks": "одностороннее расторжение заказчиком без компенсации",
            "termination": "§ 8.2, 30-дн. уведомление",
        }
