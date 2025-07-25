# ---------- Build stage: ставим зависимости ----------
FROM python:3.11-slim AS builder

ARG POETRY_VERSION=1.8.2
ARG PIP_VERSION=24.0
ARG BUILD_DATE
ARG VCS_REF
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=${POETRY_VERSION}

# Системные пакеты, которые реже всего меняются
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        libgl1-mesa-glx \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Обновляем базовые инструменты Python
RUN pip install --no-cache-dir "pip==${PIP_VERSION}" setuptools wheel

# Ставим Poetry и настраиваем на «без venv»
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
 && poetry config virtualenvs.create false

# Копируем только файлы зависимости для использования слоя-кэша
COPY pyproject.toml poetry.lock* ./

# Устанавливаем прод-зависимости;
RUN poetry install --without dev --no-interaction --no-ansi

# Poetry не ставит бинарники gunicorn/celery, поэтому добавляем их pip’ом
RUN pip install --no-cache-dir gunicorn celery

# Чистим кеши — итоговый слой ощутимо меньше
RUN poetry cache clear --all pypi && rm -rf /root/.cache/pip

# ---------- Runtime stage: минимальный образ ----------
FROM python:3.11-slim

# Только необходимые runtime-библиотеки (OpenCV/Torch → libgl, OCR → libglib)
# tini для корректной обработки сигналов в Docker
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        tini \
        && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    BUILD_DATE=${BUILD_DATE} \
    VCS_REF=${VCS_REF}

WORKDIR /app

# Переносим установленные пакеты и бинарники из сборочного слоя
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/poetry     /usr/local/bin/poetry
COPY --from=builder /usr/local/bin/gunicorn   /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/celery     /usr/local/bin/celery

# Копируем исходный код приложения (последним — для кэша)
COPY . .

# Используем непривилегированного пользователя
RUN useradd --create-home --uid 1001 appuser
USER appuser

# Открываем порт, на котором работает FastAPI-приложение
EXPOSE 8000

# Health-probe (по желанию можно удалить/изменить)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD curl -f http://localhost:8000/healthz || exit 1

# Старт: Gunicorn + UvicornWorker
ENTRYPOINT ["tini", "-g", "--"]
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.adapters.inbound.http_api:app", "--bind", "0.0.0.0:8000", "--timeout", "180"]
