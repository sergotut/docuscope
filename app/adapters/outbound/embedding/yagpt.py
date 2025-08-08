"""API-клиент Yandex GPT Embedding.

Обёртка над публичным API Yandex GPT для получения текстовых эмбеддингов.
Работает через REST-запросы к endpoint /embeddings:embedText.
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


class YAGPTEmbedding(EmbeddingPort):
    """Адаптер YaGPT Embedding.

    Работает с облачным эндпоинтом Yandex GPT.
    """

    def __init__(
        self,
        api_key: str,
        *,
        folder_id: str | None = None,
        model_name: str,
        endpoint: str,
        timeout: float = 30.0,
        batch_size: int = 1,
        space: str = "retrieval",
    ) -> None:
        """Инициализирует API-клиент Yandex GPT.

        Args:
            api_key (str): API-ключ доступа к Yandex GPT.
            folder_id (str | None): Идентификатор каталога в Yandex Cloud.
            model_name (str): Название модели.
            endpoint (str): URL эндпоинта embeddings.
            timeout (float): Таймаут для HTTP-запросов (в секундах).
            batch_size (int): Размер батча.
            space (str): Пространство (semantic, retrieval и др.).
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_name = model_name
        self.endpoint = endpoint
        self.batch_size = batch_size
        self.space = space
        
        self._client = httpx.Client(timeout=timeout)
        self._dim: int | None = None
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

        if self.folder_id:
            self.headers["X-Folder-Id"] = self.folder_id
        
        logger.info(
            "YAGPTEmbedding client init",
            model=self.model_name,
            endpoint=self.endpoint,
            folder_id=self.folder_id,
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
            logger.warning("YaGPTEmbedding health error", error=str(exc))
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
        return 1024

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
        """Синхронный REST-запрос к API YaGPT.

        Args:
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        logger.debug("YaGPTEmbedding request", cnt=len(texts), space=self.space)
        
        resp = self._client.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "texts": texts,
                "space": self.space
            },
            headers=self.headers
        )

        resp.raise_for_status()
        embeds = resp.json().get("embeddings", [])

        if embeds and self._dim is None:
            self._dim = len(embeds[0])
            logger.info("YaGPTEmbedding dim detected", dim=self._dim)

        logger.debug("YaGPTEmbedding response", embeddings=len(embeds))

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

        embeds = resp.json().get("embeddings", [])

        if embeds and self._dim is None:
            self._dim = len(embeds[0])
            logger.info("YaGPTEmbedding dim detected (async)", dim=self._dim)

        logger.debug("YaGPTEmbedding response", embeddings=len(embeds))

        return embeds

    def __del__(self) -> None:
        """Закрывает http-клиент при удалении экземпляра."""
        with contextlib.suppress(Exception):
            self._client.close()
