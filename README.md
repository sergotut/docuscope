# Документоскоп

SaaS/Telegram-сервис для анализа договоров на базе LLM.

## Быстрый старт

```bash
poetry install
cp .env.sample .env
docker-compose -f docker/docker-compose.yml up -d --build

### Настройка сплиттера

В файле `.env` задайте размеры чанков и overlap:

```env
SPLITTER_MAX_TOKENS=512   # токенов cl100k в чанке
SPLITTER_OVERLAP=64       # токенов пересечения

