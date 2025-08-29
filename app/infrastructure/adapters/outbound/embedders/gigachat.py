"""API-клиент GigaChat Embedder.

Реализует EmbedderPort: асинхронный расчёт эмбеддингов батчами и health-report.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Final

import httpx
import structlog

from app.domain.model.diagnostics import EmbedderHealthReport
from app.domain.model.retrieval import EmbeddingBatch, EmbeddingVector
from app.domain.ports import EmbedderPort

__all__ = ["SberGigaChatEmbedder"]

logger = structlog.get_logger(__name__)

_DEFAULT_TIMEOUT: Final[float] = 30.0


class SberGigaChatEmbedder(EmbedderPort):
    """Адаптер GigaChat Embeddings API.

    Attributes:
        api_key (str): OAuth-токен доступа к GigaChat API.
        model_name (str): Имя модели эмбеддингов (например, embedding-v1).
        endpoint (str): URL эндпоинта эмбеддингов.
        timeout (float): Таймаут HTTP-запросов (секунды).
        batch_size (int): Размер батча.
        max_tokens (int): Максимальная длина входа в токенах (хинт).
    """

    def __init__(
        self,
        api_key: str,
        *,
        model_name: str = "embedding-v1",
        endpoint: str,
        timeout: float = _DEFAULT_TIMEOUT,
        batch_size: int = 1,
        max_tokens: int = 2048,
    ) -> None:
        """Создаёт клиент GigaChat Embeddings.

        Args:
            api_key (str): OAuth-токен доступа к GigaChat API.
            model_name (str): Название модели (по умолчанию embedding-v1).
            endpoint (str): URL эндпоинта эмбеддингов.
            timeout (float): Таймаут HTTP-запросов (секунды).
            batch_size (int): Размер батча.
            max_tokens (int): Максимальная длина входа в токенах (хинт).
        """
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = endpoint.rstrip("/")
        self.timeout = float(timeout)
        self.batch_size = int(batch_size)
        self._max_tokens = int(max_tokens)

        self._dim: int = 0

        logger.info(
            "GigaChat embedder init",
            model=self.model_name,
            endpoint=self.endpoint,
            timeout=self.timeout,
            batch_size=self.batch_size,
            max_tokens=self._max_tokens,
        )

    async def embed(
        self,
        *,
        texts: list[str],
    ) -> EmbeddingBatch:
        """Вычисляет эмбеддинги для набора строк.

        Args:
            texts (list[str]): Входные строки.

        Returns:
            EmbeddingBatch: Батч эмбеддингов в исходном порядке.

        Raises:
            httpx.HTTPError: Если HTTP-запрос завершился ошибкой.
            ValueError: Если ответ сервера имеет некорректный формат.
        """
        if not texts:
            return EmbeddingBatch(vectors=())

        vectors: list[EmbeddingVector] = []
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as cli:
            for batch in self._chunks(texts):
                embeds = await self._embed_once_async(cli, batch)

                if self._dim <= 0 and embeds:
                    self._dim = len(embeds[0])

                    logger.info("GigaChat embedding dim detected", dim=self._dim)

                vectors.extend(
                    EmbeddingVector(values=tuple(map(float, vec))) for vec in embeds
                )

        return EmbeddingBatch(vectors=tuple(vectors))

    async def is_healthy(self) -> bool:
        """Короткий health-check на основе ответа API.

        Returns:
            bool: True, если запрос/парсинг выполняются без ошибок.
        """
        try:
            report = await self.health()

            return bool(report.get("dim", 0) > 0)
        except Exception:  # noqa: BLE001
            return False

    async def health(self) -> EmbedderHealthReport:
        """Подробный health-репорт.

        Returns:
            EmbedderHealthReport: Метаинформация о состоянии эмбеддера.
        """
        dim = self._dim
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as cli:
                embeds = await self._embed_once_async(cli, ["ping"])

            if embeds:
                dim = len(embeds[0])
        except Exception as exc:  # noqa: BLE001
            logger.warning("GigaChat health probe failed", error=str(exc))

        return {
            "model": self.model_name,
            "dim": int(dim),
            "framework": "gigachat",
            "device": "remote",
            "version": "unknown",
        }

    @property
    def preferred_batch_size(self) -> int:
        """Предпочтительный размер батча.

        Returns:
            int: Размер батча.
        """
        return self.batch_size

    @property
    def embedding_dim(self) -> int:
        """Размерность выходного эмбеддинга.

        Returns:
            int: Размерность вектора.
        """
        return self._dim

    @property
    def max_tokens(self) -> int:
        """Максимальное количество токенов на вход.

        Returns:
            int: Лимит токенов.
        """
        return self._max_tokens

    async def _embed_once_async(
        self,
        cli: httpx.AsyncClient,
        texts: list[str],
    ) -> list[list[float]]:
        """Асинхронный REST-запрос к GigaChat API.

        Args:
            cli (httpx.AsyncClient): Преднастроенный HTTP-клиент.
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Список эмбеддингов.

        Raises:
            httpx.HTTPError: Если HTTP-запрос завершился ошибкой.
            ValueError: Если ответ сервера не содержит данных.
        """
        payload: dict[str, object] = {
            "model": self.model_name,
            "input": texts,
        }

        logger.debug("GigaChat embeddings request", items=len(texts))

        resp = await cli.post(self.endpoint, json=payload)
        resp.raise_for_status()

        data = resp.json()
        items = data.get("data")

        if not isinstance(items, list):
            raise ValueError("Invalid embeddings response: no 'data' list")

        try:
            vectors = [item["embedding"] for item in items]
        except Exception as exc:  # noqa: BLE001
            logger.warning("GigaChat invalid response schema", error=str(exc))
            raise ValueError("Invalid embeddings schema") from exc

        logger.debug("GigaChat embeddings ok", items=len(vectors))

        return vectors

    def _chunks(self, seq: list[str]) -> Iterator[list[str]]:
        """Разбивает входной список на батчи.

        Args:
            seq (list[str]): Список строк.

        Returns:
            Iterator[list[str]]: Итератор по батчам.
        """
        for i in range(0, len(seq), self.batch_size):
            yield seq[i : i + self.batch_size]
