"""Sentence-Transformers адаптер, реализующий EmbeddingPort.

Позволяет рассчитывать эмбеддинги с помощью любой модели из библиотеки
sentence-transformers. Поддерживает квантованные модели, асинхронный режим и
автоматическую перезагрузку локальных весов при изменении.
"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from collections.abc import Iterator

import structlog
import torch
from sentence_transformers import SentenceTransformer

from app.core.ports import EmbeddingPort

logger = structlog.get_logger(__name__)


class SentenceTransformersEmbedding(EmbeddingPort):
    """Адаптер Sentence Transformers."""

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        batch_size: int = 1,
        space: str = "retrieval",
        dtype: str = "float32",
        quantized: bool = False,
        max_tokens: int = 512
    ) -> None:
        """Инициализирует адаптер SentenceTransformers.

        Args:
            model_name (str): Название модели или путь к локальной директории.
            device (str | None): Устройство инференса (cpu/cuda).
            batch_size (int): Размер батча.
            space (str): Пространство (semantic, retrieval и др.).
            dtype (str): Тип тензора ('float32', 'float16', 'bfloat16').
            quantized (bool): Загружать модель в 8-битном режиме (через bitsandbytes).
            max_tokens (int): Максимальное количество токенов.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        self.space = space
        self.dtype = getattr(torch, dtype, torch.float32)
        self.quantized = quantized

        self._model_load_time = 0.0
        self._model_mtime = 0.0
        self._dim: int | None = None
        self._max_tokens = max_tokens
        self._load_model()

        logger.info(
            "ST Embedding client init",
            model=self.model_name,
            device=self.device,
            dtype=self.dtype,
            quantized=self.quantized
        )

    def embed(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """Синхронное получение эмбеддингов.

        Args:
            texts (list[str]): Список входных строк.

        Returns:
            list[list[float]]: Вектора-эмбеддинги.
        """
        self._reload_if_changed()
        logger.debug("ST Embedding request", cnt=len(texts), space=self.space)

        embeds: list[list[float]] = []

        for batch in self._chunks(texts):
            batch_emb = self._model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False,
                device=self.device,
            )

            if self._dim is None:
                self._dim = len(batch_emb[0])
                logger.info("ST Embedding dim detected", dim=self._dim)

            embeds.extend(batch_emb.tolist())

        return embeds

    async def embed_async(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """Асинхронная версия embed с run_in_executor.

        Args:
            texts (list[str]): Список строк.

        Returns:
            list[list[float]]: Эмбеддинги.
        """
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(None, self.embed, texts)

    def is_healthy(self) -> bool:
        """Короткий health-check на основе метода 'health'.

        Returns:
            bool: True, если статус "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, str | int | float]:
        """Подробный health-репорт.

        Returns:
            dict: Метрики — статус, latency, модель, размерность.
        """
        start = time.perf_counter()
        
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("ST health error", error=str(exc))
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": self._dim or -1,
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
        return self._max_tokens

    def _load_model(self) -> None:
        """Загружает модель и инициализирует метаинформацию."""
        logger.info(
            "Загрузка SentenceTransformer",
            model=self.model_name,
            device=self.device,
            quantized=self.quantized,
        )
        start = time.perf_counter()

        extra_args = {}
        if self.quantized:
            extra_args = {"device_map": "auto", "load_in_8bit": True}

        self._model = SentenceTransformer(
            self.model_name,
            device=self.device,
            **extra_args,
        )
        
        self._model_load_time = time.perf_counter() - start
        
        if os.path.isdir(self.model_name):
            self._model_mtime = Path(self.model_name).stat().st_mtime
        self._dim = self._model.get_sentence_embedding_dimension()
        
        logger.info(
            "SentenceTransformer загружен",
            load_time_s=round(self._model_load_time, 2),
            dim=self._dim,
        )

    def _reload_if_changed(self) -> None:
        """Перезагружает модель, если обновились веса в папке."""
        if not os.path.isdir(self.model_name):
            return
        mtime = Path(self.model_name).stat().st_mtime
        
        if mtime > self._model_mtime:
            logger.info(
                "ST Embeddnig: Обнаружены изменения модели, перезагрузка"
            )
            self._load_model()

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
