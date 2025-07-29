"""API-клиент GigaChat Embedding.

Отправляет запросы на эндпоинт GigaChat для получения эмбеддингов.
Реализует протокол EmbeddingPort и поддерживает sync/async интерфейсы.
"""

from __future__ import annotations

import asyncio
import contextlib
import time

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
        model_name: str = "embedding-v1",
        endpoint: str = _ENDPOINT,
        timeout: float = 30.0,
    ) -> None:
        """Инициализирует клиент GigaChat Embedding.

        Args:
            api_key (str): OAuth-токен доступа к GigaChat API.
            model_name (str): Название модели (по умолчанию embedding-v1).
            endpoint (str): URL эндпоинта.
            timeout (float): Таймаут HTTP-запросов.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = endpoint.rstrip("/")
        self._client = httpx.Client(timeout=timeout)
        self._dim: int | None = None

        logger.info(
            "GigaChat client init",
            model=model_name,
            endpoint=self.endpoint,
        )

    def embed(self, texts: list[str], space: str = "semantic") -> list[list[float]]:
        """Синхронный вызов эмбеддингов через GigaChat API.

        Args:
            texts (list[str]): Список строк для кодирования.
            space (str): Тип пространства (semantic и т.д.).

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        hdr = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.debug("GigaChat request", cnt=len(texts), space=space)
        
        resp = self._client.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "input": texts,
                "space": space
            },
            headers=hdr
        )

        resp.raise_for_status()
        embeds = [d["embedding"] for d in resp.json().get("data", [])]

        if embeds and self._dim is None:
            self._dim = len(embeds[0])
            logger.info("GigaChat dim detected", dim=self._dim)

        logger.debug("GigaChat response", embeddings=len(embeds))
        return embeds

    async def embed_async(
        self, texts: list[str], space: str = "semantic"
    ) -> list[list[float]]:
        """Асинхронный вызов эмбеддингов.

        Args:
            texts (list[str]): Список строк.
            space (str): Тип пространства (semantic и пр.).

        Returns:
            list[list[float]]: Эмбеддинги.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.embed, texts, space)

    def is_healthy(self) -> bool:  # noqa: D401
        """Короткий health-check.

        Returns:
            bool: True, если ответ успешен.
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, str | int | float]:
        """Подробный отчёт о доступности GigaChat.

        Returns:
            dict: Метрики: статус, latency, модель, размерность.
        """
        start = time.perf_counter()
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("GigaChat health error", error=str(exc))
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": self._dim or -1
        }

    def __del__(self) -> None:
        """Закрывает HTTP-клиент при удалении экземпляра."""
        with contextlib.suppress(Exception):
            self._client.close()
