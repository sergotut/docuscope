"""API-клиент Yandex GPT Embedder.

Реализует EmbedderPort: асинхронный расчёт эмбеддингов батчами и health-report.
"""

from __future__ import annotations

from collections.abc import Iterator

import httpx
import structlog

from app.domain.model.diagnostics import EmbedderHealthReport
from app.domain.model.retrieval import EmbeddingBatch, EmbeddingVector
from app.domain.ports import EmbedderPort

__all__ = ["YAGPTEmbedder"]

logger = structlog.get_logger(__name__)


class YAGPTEmbedder(EmbedderPort):
    """Адаптер Yandex GPT Embeddings API.

    Attributes:
        api_key (str): API-ключ доступа к Yandex GPT.
        folder_id (str | None): Идентификатор каталога в Yandex Cloud.
        model_name (str): Название модели эмбеддингов.
        endpoint (str): URL эндпоинта эмбеддингов.
        timeout (float): Таймаут HTTP-запросов (в секундах).
        batch_size (int): Размер батча.
        max_tokens (int): Максимальная длина входа в токенах (хинт).
    """

    def __init__(
        self,
        api_key: str,
        *,
        folder_id: str | None = None,
        model_name: str = "embedding",
        endpoint: str,
        timeout: float = 30.0,
        batch_size: int = 1,
        max_tokens: int = 1024,
    ) -> None:
        """Инициализирует API-клиент Yandex GPT Embeddings.

        Args:
            api_key (str): API-ключ доступа к Yandex GPT.
            folder_id (str | None): Идентификатор каталога в Yandex Cloud.
            model_name (str): Название модели эмбеддингов.
            endpoint (str): URL эндпоинта эмбеддингов.
            timeout (float): Таймаут HTTP-запросов (в секундах).
            batch_size (int): Размер батча.
            max_tokens (int): Максимальная длина входной последовательности.
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_name = model_name
        self.endpoint = endpoint.rstrip("/")
        self.timeout = float(timeout)
        self.batch_size = int(batch_size)
        self._max_tokens = int(max_tokens)

        self._dim: int = 0

        logger.info(
            "YaGPT embedder init",
            model=self.model_name,
            endpoint=self.endpoint,
            folder_id=self.folder_id,
            timeout=self.timeout,
            batch_size=self.batch_size,
            max_tokens=self._max_tokens,
        )

    async def embed(self, texts: list[str], *,) -> EmbeddingBatch:
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

        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.folder_id:
            headers["X-Folder-Id"] = self.folder_id

        vectors: list[EmbeddingVector] = []

        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as cli:
            for batch in self._chunks(texts):
                embeds = await self._embed_once_async(cli, batch)

                if self._dim <= 0 and embeds:
                    self._dim = len(embeds[0])
                    logger.info("YaGPT embedding dim detected", dim=self._dim)

                vectors.extend(
                    EmbeddingVector(values=tuple(map(float, vec))) for vec in embeds
                )

        return EmbeddingBatch(vectors=tuple(vectors))

    async def is_healthy(self) -> bool:
        """Короткий health-check.

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
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.folder_id:
            headers["X-Folder-Id"] = self.folder_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as cli:
                embeds = await self._embed_once_async(cli, ["ping"])

            if embeds:
                dim = len(embeds[0])
        except Exception as exc:  # noqa: BLE001
            logger.warning("YaGPT health probe failed", error=str(exc))

        return {
            "model": self.model_name,
            "dim": int(dim),
            "framework": "yagpt",
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

    # ----------------------------- Internals -------------------------------

    async def _embed_once_async(
        self,
        cli: httpx.AsyncClient,
        texts: list[str],
    ) -> list[list[float]]:
        """Асинхронный REST-запрос к API Yandex GPT.

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
            "texts": texts,
        }

        logger.debug("YaGPT embeddings request", items=len(texts))

        resp = await cli.post(self.endpoint, json=payload)
        resp.raise_for_status()

        data = resp.json()
        # Некоторые версии API возвращают {"embeddings": [[...], ...]}
        items = data.get("embeddings")

        if not isinstance(items, list):
            # Либо OpenAI-совместимый ответ {"data": [{"embedding": [...]}, ...]}
            alt = data.get("data")

            if isinstance(alt, list):
                try:
                    items = [d["embedding"] for d in alt]
                except Exception as exc:  # noqa: BLE001
                    logger.warning("YaGPT invalid schema", error=str(exc))
                    raise ValueError("Invalid embeddings schema") from exc
            else:
                raise ValueError("Invalid embeddings response: no embeddings/data")

        logger.debug("YaGPT embeddings ok", items=len(items))

        return items  # type: ignore[return-value]

    def _chunks(self, seq: list[str]) -> Iterator[list[str]]:
        """Разбивает входной список на батчи.

        Args:
            seq (list[str]): Список строк.

        Returns:
            Iterator[list[str]]: Итератор по батчам.
        """
        for i in range(0, len(seq), self.batch_size):
            yield seq[i : i + self.batch_size]
