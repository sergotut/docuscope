"""REST-клиент llama.cpp для модели E5-Mistral.

Отправляет запросы на эндпоинт /embeddings совместимого сервера LLM (llama.cpp).
Реализует протокол EmbeddingPort и поддерживает sync/async интерфейсы.
"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, List

import httpx
import structlog

from app.core.ports import EmbeddingPort

logger = structlog.get_logger(__name__)


class E5MistralEmbedding(EmbeddingPort):
    """Адаптер E5 Mistral Embedding.

    Работает с эндпоинтом /embeddings в llama.cpp.
    """

    def __init__(self, host: str, model_name: str, timeout: float = 30.0) -> None:
        """Создаёт клиент для REST-эндпоинта эмбеддинга.

        Args:
            host (str): Базовый URL до llama.cpp.
            model_name (str): Имя модели для передачи в payload.
            timeout (float): Таймаут для http-запросов (в секундах).
        """
        self.host = host.rstrip("/")
        self.model_name = model_name
        self._client = httpx.Client(timeout=timeout)

    def embed(self, texts: list[str], space: str = "semantic") -> List[List[float]]:
        """Выполняет sync-запрос на расчёт эмбеддингов.

        Args:
            texts (list[str]): Список строк для кодирования.
            space (str): Тип пространства (semantic и пр., игнорируется).

        Returns:
            List[List[float]]: Список эмбеддингов.
        """
        payload = {"model": self.model_name, "input": texts}
        resp = self._client.post(f"{self.host}/embeddings", json=payload)
        resp.raise_for_status()
        return [d["embedding"] for d in resp.json().get("data", [])]

    async def embed_async(
        self, texts: list[str], space: str = "semantic"
    ) -> List[List[float]]:
        """Асинхронный вызов через run_in_executor.

        Args:
            texts (list[str]): Список строк.
            space (str): Тип пространства (игнорируется).

        Returns:
            List[List[float]]: Эмбеддинги.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.embed, texts, space)

    def is_healthy(self) -> bool:  # noqa: D401
        """Короткий health-check на основе метода 'health'.

        Returns:
            bool: True, если статус "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> Dict[str, str | int | float]:
        """Расширенный health-репорт со статистикой.

        Returns:
            dict: Метрики — статус, latency, модель, размерность.
        """
        start = time.perf_counter()
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception:  # noqa: BLE001
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": 768
        }

    def __del__(self) -> None:
        """Закрывает httpx-клиент при удалении."""
        try:
            self._client.close()
        except Exception:  # noqa: BLE001
            pass
