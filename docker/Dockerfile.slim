FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main

COPY app app
COPY scripts scripts
COPY .env.sample .env

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
