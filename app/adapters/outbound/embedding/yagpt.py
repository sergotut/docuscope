"""API-клиент Yandex GPT Embedding.

Обёртка над публичным API Yandex GPT для получения текстовых эмбеддингов.
Работает через REST-запросы к endpoint /embeddings:embedText.
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

_ENDPOINT = (
    "https://llm.api.cloud.yandex.net/foundationModels/v1/embeddings:embedText"
)


class YAGPTEmbedding(EmbeddingPort):
    """Адаптер YaGPT Embedding.

    Работает с облачным эндпоинтом Yandex GPT.
    """

    def __init__(
        self,
        api_key: str,
        *,
        folder_id: str | None = None,
        model_name: str = "text-search-large-v1",
        endpoint: str = _ENDPOINT,
        timeout: float = 30.0,
    ) -> None:
        """Инициализирует API-клиент Yandex GPT.

        Args:
            api_key (str): API-ключ доступа к Yandex GPT.
            folder_id (str | None): Идентификатор каталога в Yandex Cloud.
            model_name (str): Название модели (по умолчанию text-search-large-v1).
            endpoint (str): URL эндпоинта embeddings.
            timeout (float): Таймаут для HTTP-запросов (в секундах).
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_name = model_name
        self.endpoint = endpoint
        self._client = httpx.Client(timeout=timeout)
        self._dim: int | None = None
        logger.info(
            "YAGPTEmbedding init",
            model=model_name,
            endpoint=self.endpoint,
            folder_id=folder_id,
        )

    def embed(self, texts: list[str], space: str = "semantic") -> list[list[float]]:
        """Синхронный вызов эмбеддингов через REST.

        Args:
            texts (list[str]): Список текстов.
            space (str): Тип пространства (semantic, retrieval и т.д.).

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        hdr = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

        if self.folder_id:
            hdr["X-Folder-Id"] = self.folder_id

        logger.debug("YaGPT request", cnt=len(texts), space=space)
        
        resp = self._client.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "texts": texts,
                "space": space
            },
            headers=hdr
        )

        resp.raise_for_status()
        embeds = resp.json().get("embeddings", [])

        if embeds and self._dim is None:
            self._dim = len(embeds[0])
            logger.info("YaGPT dim detected", dim=self._dim)

        logger.debug("YaGPT response", embeddings=len(embeds))

        return embeds

    async def embed_async(
        self, texts: list[str], space: str = "semantic"
    ) -> list[list[float]]:
        """Асинхронный вызов эмбеддингов.

        Args:
            texts (list[str]): Список текстов.
            space (str): Тип пространства (semantic и др.).

        Returns:
            list[list[float]]: Список эмбеддингов.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.embed, texts, space)

    def is_healthy(self) -> bool:  # noqa: D401
        """Короткий health-check на основе ответа API.

        Returns:
            bool: True, если статус "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, str | int | float]:
        """Подробный health-репорт по доступности API.

        Returns:
            dict: Метрики — статус, latency, модель, размерность.
        """
        start = time.perf_counter()
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception:  # noqa: BLE001
            logger.warning("YaGPT health error", error=str(exc))
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": self._dim or -1
        }

    def __del__(self) -> None:
        """Закрывает http-клиент при удалении экземпляра."""
        with contextlib.suppress(Exception):
            self._client.close()
