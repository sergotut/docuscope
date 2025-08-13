"""Адаптер токенайзера на базе tiktoken.

Реализует TokenizerPort: подсчёт токенов и health-report.
"""

from __future__ import annotations

import structlog
import tiktoken

from app.domain.model.diagnostics import TokenizerHealthReport
from app.domain.model.shared import TokenCount
from app.domain.ports import TokenizerPort
from .protocols import EncoderLike

__all__ = ["TiktokenTokenizer"]

logger = structlog.get_logger(__name__)


class TiktokenTokenizer(TokenizerPort):
    """Адаптер tiktoken.

    Attributes:
        model_name (str | None): Имя модели для подбора кодировки.
        encoding_name (str): Имя кодировки tiktoken.
    """

    __slots__ = ("_model_name", "_encoding_name", "_enc")

    def __init__(
        self,
        model_name: str | None = None,
        *,
        encoding_name: str | None = None,
    ) -> None:
        """Создаёт токенайзер.

        Args:
            model_name (str | None): Имя модели для encoding_for_model.
            encoding_name (str | None): Явное имя кодировки tiktoken.
        """
        self._model_name = model_name
        self._encoding_name = self._resolve_encoding_name(
            model_name=model_name,
            encoding_name=encoding_name,
        )
        self._enc: EncoderLike = self._build_encoder(self._encoding_name)

        logger.info(
            "tiktoken tokenizer init",
            model=self._model_name,
            encoding=self._encoding_name,
            tiktoken_version=getattr(tiktoken, "__version__", "unknown"),
        )

    def count_tokens(self, text: str) -> TokenCount:
        """Возвращает количество токенов в строке.

        Args:
            text (str): Входной текст.

        Returns:
            TokenCount: Количество токенов.
        """
        return TokenCount(len(self._enc.encode(text)))

    def is_healthy(self) -> bool:
        """Короткий health-check на основе метода health.

        Returns:
            bool: True, если размер словаря больше нуля.
        """
        try:
            report = self.health()

            return "vocab_size" in report and report["vocab_size"] > 0
        except Exception:  # noqa: BLE001
            return False

    def health(self) -> TokenizerHealthReport:
        """Расширенный health-report.

        Returns:
            TokenizerHealthReport: Метаинформация о состоянии токенайзера.
        """
        try:
            vocab_size = int(self._enc.n_vocab)

            return {
                "model": self._model_name or "unknown",
                "vocab_size": vocab_size,
                "encoding": self._encoding_name,
                "version": getattr(tiktoken, "__version__", "unknown"),
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("tiktoken health error", error=str(exc))

            return {
                "model": self._model_name or "unknown",
                "vocab_size": 0,
                "encoding": self._encoding_name,
                "version": getattr(tiktoken, "__version__", "unknown"),
            }

    @staticmethod
    def _resolve_encoding_name(
        *,
        model_name: str | None,
        encoding_name: str | None,
    ) -> str:
        """Определяет имя кодировки tiktoken.

        Приоритет:
            1) encoding_name;
            2) encoding_for_model(model_name);
            3) cl100k_base.

        Args:
            model_name (str | None): Имя модели для подбора кодировки.
            encoding_name (str | None): Явное имя кодировки.

        Returns:
            str: Имя кодировки tiktoken.
        """
        if encoding_name:
            return encoding_name
        if model_name:
            try:
                enc = tiktoken.encoding_for_model(model_name)

                return getattr(enc, "name", "cl100k_base")
            except Exception:  # noqa: BLE001
                logger.debug("fallback: unknown tiktoken model", model=model_name)

        return "cl100k_base"

    @staticmethod
    def _build_encoder(encoding_name: str) -> EncoderLike:
        """Создаёт энкодер по имени кодировки.

        Args:
            encoding_name (str): Имя кодировки tiktoken.

        Returns:
            EncoderLike: Экземпляр энкодера.
        """
        try:
            return tiktoken.get_encoding(encoding_name)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "unknown tiktoken encoding, fallback to cl100k_base",
                encoding=encoding_name,
                error=str(exc),
            )

            return tiktoken.get_encoding("cl100k_base")
