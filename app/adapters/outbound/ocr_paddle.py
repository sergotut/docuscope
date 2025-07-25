import structlog

logger = structlog.get_logger()


class PaddleOCRAdapter:
    def __init__(self):
        pass

    def ocr(self, image_bytes) -> str:
        logger.debug("ocr_start")
        return "распознанный текст"
