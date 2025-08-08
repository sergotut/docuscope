"""REST-клиент llama.cpp для модели E5-Mistral.

Отправляет запросы на эндпоинт /embeddings совместимого сервера LLM (llama.cpp).
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


class E5MistralEmbedding(EmbeddingPort):
    """Адаптер E5 Mistral Embedding.

    Работает с эндпоинтом /embeddings в llama.cpp.
    """

    def __init__(
        self,
        host: str,
        port: str,
        model_name: str,
        timeout: float = 30.0,
        batch_size: int = 1,
        space: str = "retrieval",
        dim: int = 768
    ) -> None:
        """Создаёт клиент для REST-эндпоинта эмбеддинга.

        Args:
            host (str): Базовый URL до llama.cpp.
            port (str): Базовый порт llama.cpp.
            model_name (str): Имя модели для передачи в payload.
            timeout (float): Таймаут для http-запросов (в секундах).
            batch_size (int): Размер батча.
            space (str): Пространство (semantic, retrieval и др.).
            dim (int): Размерность модели.
        """
        self.host = host.rstrip("/")
        self.port = port,
        self.url = f"{self.host}:{self.port}",
        self.url_embeddings = f"{self.url}/embeddings",
        self.model_name = model_name
        self.batch_size = batch_size
        self.space = space
        self._client = httpx.Client(timeout=timeout)
        self._dim = dim

        logger.info("E5 Embedding client init", model=model_name, url=self.url)

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
        """Короткий health-check на основе метода 'health'.

        Returns:
            bool: True, если статус "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, str | int | float]:
        """Подробный health-репорт со статистикой.

        Returns:
            dict[str, str | int | float]: Метрики — статус, latency, модель,
                размерность.
        """
        start = time.perf_counter()
        
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("E5 health error", error=str(exc))
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": self.dim
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
        return 512

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
        """Синхронный запрос на расчёт эмбеддингов.

        Args:
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        logger.debug("E5 Embedding request", cnt=len(texts), space=self.space)

        resp = self._clinet.post(
            url=self.url_embeddings,
            json={
                "model": self.model_name,
                "input": texts
            }
        )

        resp.raise_for_status()
        embeds = [d["embedding"] for d in resp.json().get("data", [])]

        logger.debug("E5 Embedding response", embeddings=len(embeds))

        return embeds

    async def _embed_once_async(
        self,
        cli: httpx.AsyncClient,
        texts: list[str]
    ) -> list[list[float]]:
        """Асинхронный запрос на расчёт эмбеддингов.

        Args:
            cli (httpx.AsyncClient): Клиент HTTPX.
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        resp = await cli.post(
            url=self.url_embeddings,
            json={
                "model": self.model_name,
                "input": texts
            }
        )

        resp.raise_for_status()
        embeds = [d["embedding"] for d in resp.json().get("data", [])]

        logger.debug("E5 Embedding response", embeddings=len(embeds))

        return embeds

    def __del__(self) -> None:
        """Закрывает httpx-клиент при удалении."""
        with contextlib.suppress(Exception):
            self._client.close()
