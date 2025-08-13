"""REST-адаптер эмбеддеров для модели E5-Mistral (llama.cpp).

Реализует EmbedderPort: асинхронный расчёт эмбеддингов батчами и health-report.
Ожидается эндпоинт /embeddings на стороне сервера (например, llama.cpp).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Final

import httpx
import structlog

from app.domain.model.diagnostics import EmbedderHealthReport
from app.domain.model.retrieval import EmbeddingBatch, EmbeddingVector
from app.domain.ports import EmbedderPort

__all__ = ["E5MistralEmbedder"]

logger = structlog.get_logger(__name__)

_DEFAULT_TIMEOUT: Final[float] = 30.0


class E5MistralEmbedder(EmbedderPort):
    """Адаптер REST-эмбеддера E5 Mistral.

    Работает с эндпоинтом /embeddings совместимого сервера (llama.cpp).

    Attributes:
        host (str): Хост со схемой или без (например, http://localhost).
        port (int): Порт сервера.
        model_name (str): Имя модели, передаваемое в payload.
        timeout (float): Таймаут для http-запросов (в секундах).
        batch_size (int): Размер батча.
        _dim (int): Размерность модели.
        _max_tokens (int): Максимальная длина входа в токенах (хинт).
    """

    def __init__(
        self,
        host: str,
        port: int,
        model_name: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        batch_size: int = 32,
        dim: int = 768,
        max_tokens: int = 512,
    ) -> None:
        """Создаёт REST-клиент эмбеддеров.

        Args:
            host (str): Базовый хост (llama.cpp).
            port (int): Порт сервиса (llama.cpp).
            model_name (str): Имя модели для передачи в payload.
            timeout (float): Таймаут для http-запросов (в секундах).
            batch_size (int): Размер батча.
            dim (int): Размерность модели.
            max_tokens (int): Максимальная длина входа в токенах (хинт).
        """
        self.host = host.rstrip("/")
        self.port = int(port)
        self.model_name = model_name
        self.timeout = float(timeout)
        self.batch_size = int(batch_size)

        self._dim: int = int(dim)
        self._max_tokens = int(max_tokens)

        scheme_host = (
            self.host
            if self.host.startswith(("http://", "https://"))
            else f"http://{self.host}"
        )
        self._base_url = f"{scheme_host}:{self.port}"
        self._embeddings_url = f"{self._base_url}/embeddings"

        logger.info(
            "E5 Mistral REST embedder init",
            model=self.model_name,
            url=self._embeddings_url,
            batch_size=self.batch_size,
            dim=self._dim,
            timeout=self.timeout,
        )

    async def embed(self, *, texts: list[str],) -> EmbeddingBatch:
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

        logger.debug("E5 embed request", count=len(texts))

        vectors: list[EmbeddingVector] = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for batch in self._chunks(texts):
                embeds = await self._embed_once_async(client, batch)

                if self._dim <= 0 and embeds:
                    self._dim = len(embeds[0])
                    logger.info("E5 embedding dim detected", dim=self._dim)

                vectors.extend(
                    EmbeddingVector(values=tuple(map(float, vec))) for vec in embeds
                )

        return EmbeddingBatch(vectors=tuple(vectors))

    async def is_healthy(self) -> bool:
        """Короткий health-check на основе метода health.

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

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                embeds = await self._embed_once_async(client, ["ping"])

            if embeds:
                dim = len(embeds[0])
        except Exception as exc:  # noqa: BLE001
            logger.warning("E5 health probe failed", error=str(exc))

        return {
            "model": self.model_name,
            "dim": int(dim),
            "framework": "llama.cpp",
            "device": "remote",
            "version": "unknown",
        }

    @property
    def preferred_batch_size(self) -> int:
        """Предпочтительный размер батча.

        Returns:
            int: Количество строк на один вызов embed.
        """
        return self.batch_size

    @property
    def embedding_dim(self) -> int:
        """Размерность выходного эмбеддинга.

        Returns:
            int: Количество элементов в одном векторе.
        """
        return self._dim

    @property
    def max_tokens(self) -> int:
        """Максимальное количество токенов на вход.

        Returns:
            int: Ограничение длины входной строки в токенах.
        """
        return self._max_tokens

    async def _embed_once_async(
        self,
        client: httpx.AsyncClient,
        texts: list[str],
    ) -> list[list[float]]:
        """Выполняет один HTTP-вызов /embeddings.

        Args:
            client (httpx.AsyncClient): HTTP-клиент.
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Сырые эмбеддинги.

        Raises:
            httpx.HTTPError: Если HTTP-запрос завершился ошибкой.
            ValueError: Если ответ сервера не содержит данных.
        """
        payload: dict[str, object] = {"model": self.model_name, "input": texts}

        resp = await client.post(self._embeddings_url, json=payload)
        resp.raise_for_status()

        data = resp.json()
        items = data.get("data")

        if not isinstance(items, list):
            raise ValueError("Invalid embeddings response: no 'data' list")

        try:
            vectors = [item["embedding"] for item in items]
        except Exception as exc:  # noqa: BLE001
            logger.warning("E5 invalid response schema", error=str(exc))
            raise ValueError("Invalid embeddings schema") from exc

        logger.debug("E5 embed batch ok", items=len(vectors))

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
