"""API-клиент GigaChat Embedding.

Отправляет запросы на эндпоинт GigaChat для получения эмбеддингов.
Реализует протокол EmbeddingPort и поддерживает sync/async интерфейсы.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from collections.abc import Iterator

import httpx
import structlog

from app.core.ports import EmbeddingPort

logger = structlog.get_logger(__name__)

_ENDPOINT = "https://api.gigachat.ru/embeddings/v1"


class SberGigaChatEmbedding(EmbeddingPort):
    """Адаптер Sber GigaChat Embedder.

    Работает с REST-эндпоинтом GigaChat.
    """

    def __init__(
        self,
        api_key: str,
        *,
        model_name: str,
        endpoint: str,
        timeout: float = 30.0,
        batch_size: int = 1,
        space: str = "retrieval",
    ) -> None:
        """Инициализирует клиент GigaChat Embedding.

        Args:
            api_key (str): OAuth-токен доступа к GigaChat API.
            model_name (str): Название модели (по умолчанию embedding-v1).
            endpoint (str): URL эндпоинта.
            timeout (float): Таймаут HTTP-запросов.
            batch_size (int): Размер батча.
            space (str): Пространство (semantic, retrieval и др.).
        """
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = endpoint
        self.batch_size = batch_size
        self._client = httpx.Client(timeout=timeout)
        self._dim: int | None = None
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info(
            "GigaChatEmbedding client init",
            model=model_name,
            endpoint=self.endpoint,
        )

    def embed(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """Синхронное получение эмбеддингов.

        Args:
            texts (list[str]): Входные строки.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        embeds_all: list[list[float]] = []
        for batch in self._chunks(texts):
            embeds_all.extend(self._embed_once(batch))
        return embeds_all

    async def embed_async(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """Асинхронный вызов эмбеддингов.

        Args:
            texts (list[str]): Список текстов.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        async with httpx.AsyncClient(timeout=self._client.timeout) as cli:
            embeds_all: list[list[float]] = []
            for batch in self._chunks(texts):
                embeds_all.extend(
                    await self._embed_once_async(cli, batch)
                )

        return embeds_all

    def is_healthy(self) -> bool:  # noqa: D401
        """Короткий health-check на основе ответа API.

        Returns:
            bool: True, если статус "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, str | int | float]:
        """Подробный health-репорт по доступности API.

        Returns:
            dict[str, str | int | float]: Метрики API.
        """
        start = time.perf_counter()
        
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("GigaChatEmbedding health error", error=str(exc))
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": self._dim or -1
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
        return self._dim or -1

    @property
    def max_tokens(self) -> int:
        """Максимальное количество токенов на вход.

        Returns:
            int: Лимит токенов.
        """
        return 2048

    def _chunks(
        self,
        seq: list[str]
    ) -> Iterator[list[str]]:
        """Разбивает входной список на батчи.

        Args:
            seq (list[str]): Список строк.

        Returns:
            list[list[str]]: Список батчей.
        """
        for i in range(0, len(seq), self.batch_size):
            yield seq[i : i + self.batch_size]

    def _embed_once(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """Синхронный REST-запрос к GigaChat API.

        Args:
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        logger.debug("GigaChatEmbedder request", cnt=len(texts), space=self.space)
        
        resp = self._client.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "input": texts,
                "space": self.space
            },
            headers=self.headers
        )

        resp.raise_for_status()
        embeds = [d["embedding"] for d in resp.json().get("data", [])]

        if embeds and self._dim is None:
            self._dim = len(embeds[0])
            logger.info("GigaChatEmbedding dim detected", dim=self._dim)

        logger.debug("GigaChatEmbedding response", embeddings=len(embeds))
        
        return embeds

    async def _embed_once_async(
        self,
        cli: httpx.AsyncClient,
        texts: list[str]
    ) -> list[list[float]]:
        """Асинхронный REST-запрос к API YaGPT.

        Args:
            cli (httpx.AsyncClient): Клиент HTTPX.
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        resp = await cli.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "texts": texts,
                "space": self.space
            },
            headers=self.headers,
        )
        resp.raise_for_status()

        embeds = [d["embedding"] for d in resp.json().get("data", [])]

        if embeds and self._dim is None:
            self._dim = len(embeds[0])
            logger.info("GigaChatEmbedding dim detected", dim=self._dim)

        logger.debug("GigaChatEmbedding response", embeddings=len(embeds))
    
        return embeds

    def __del__(self) -> None:
        """Закрывает HTTP-клиент при удалении экземпляра."""
        with contextlib.suppress(Exception):
            self._client.close()
