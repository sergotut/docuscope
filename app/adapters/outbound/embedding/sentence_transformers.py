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

import structlog
import torch
from sentence_transformers import SentenceTransformer

from app.core.ports import EmbeddingPort

logger = structlog.get_logger(__name__)


class SentenceTransformersEmbedding(EmbeddingPort):
    """Адаптер Sentence Transformers."""

    _dim: int | None = None

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        batch_size: int = 32,
        dtype: str = "float32",
        quantized: bool = False,
    ) -> None:
        """Инициализирует адаптер SentenceTransformers.

        Args:
            model_name (str): Название модели или путь к локальной директории.
            device (str | None): Устройство инференса (cpu/cuda).
            batch_size (int): Размер батча для инференса.
            dtype (str): Тип тензора ('float32', 'float16', 'bfloat16').
            quantized (bool): Загружать модель в 8-битном режиме (через bitsandbytes).
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = getattr(torch, dtype, torch.float32)
        self.quantized = quantized

        self._model_load_time = 0.0
        self._model_mtime = 0.0
        self._load_model()

    def embed(self, texts: list[str], space: str = "semantic") -> list[list[float]]:
        """Синхронный подсчёт эмбеддингов.

        Args:
            texts (list[str]): Список входных строк.
            space (str): Тип пространства (semantic, retrieval и пр.).

        Returns:
            list[list[float]]: Вектора-эмбеддинги.
        """
        self._reload_if_changed()
        logger.debug("ST embed", cnt=len(texts), space=space)
        embeddings: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_emb = self._model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False,
                device=self.device,
            )
            if self._dim is None:
                self._dim = len(batch_emb[0])
            embeddings.extend(batch_emb.tolist())

        return embeddings

    async def embed_async(
        self, texts: list[str], space: str = "semantic"
    ) -> list[list[float]]:
        """Асинхронная версия embed с run_in_executor.

        Args:
            texts (list[str]): Список строк.
            space (str): Тип пространства (по умолчанию semantic).

        Returns:
            list[list[float]]: Эмбеддинги.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.embed, texts, space)

    def is_healthy(self) -> bool:
        """Короткий health-check на основе метода 'health'.

        Returns:
            bool: True, если статус "ok".
        """
        return self.health().get("status") == "ok"

    def health(self) -> dict[str, str | int | float]:
        """Расширенный health-репорт со статистикой.

        Returns:
            dict: Метрики — статус, latency, модель, размерность.
        """
        start = time.perf_counter()
        try:
            _ = self.embed(["ping"])
            latency = (time.perf_counter() - start) * 1000
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.warning("ST health fail", error=str(exc))
            latency = -1.0
            status = "fail"
        return {
            "status": status,
            "latency_ms": round(latency, 2),
            "model": self.model_name,
            "dim": self._dim or -1,
        }

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
            logger.info("Обнаружены изменения модели, перезагрузка")
            self._load_model()
