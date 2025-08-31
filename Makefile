# ===== Variables =====
# --- Poetry discovery & PATH for non-interactive shells ---
SHELL := /bin/bash
export PATH := $(HOME)/.local/bin:$(PATH)

POETRY := $(shell command -v poetry 2>/dev/null || echo "$(HOME)/.local/bin/poetry")
PY := $(POETRY) run

PY ?= poetry run
PKG_DIR ?= app
COV_MIN ?= 90

# docker / ghcr
OWNER ?= $(shell git config --get remote.origin.url | sed -E 's#.*[:/](.+)/.+\.git#\1#')
IMAGE ?= ghcr.io/$(OWNER)/docuscope
COMMIT ?= $(shell git rev-parse --short HEAD)

# compose (v2)
COMPOSE ?= docker compose

# BuildKit faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# ===== Phony =====
.PHONY: help dev up down logs test lint fmt black ruff typecheck coverage \
        qa precommit build publish sbom trivy migrate seed

poetry_check:
	@if [ ! -x "$(POETRY)" ]; then \
	  echo "Poetry не найден в $$PATH."; \
	  echo "Установи его и добавь в PATH:"; \
	  echo '  curl -sSL https://install.python-poetry.org | python3 -'; \
	  echo '  echo '\"export PATH=\$$HOME/.local/bin:\$$PATH\"' >> ~/.zprofile && source ~/.zprofile'; \
	  exit 127; \
	fi

help: ## Показать список целей
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	 sed -E 's/:.*?##/: /' | sort

# ===== Dev / Compose =====
dev: ## Локальная разработка (foreground)
	$(COMPOSE) -f docker/docker-compose-local.yml up --build

up: ## Поднять сервисы в фоне
	$(COMPOSE) -f docker/docker-compose.yml up -d --build

down: ## Остановить сервисы
	$(COMPOSE) -f docker/docker-compose.yml down

logs: ## Логи docker compose
	$(COMPOSE) -f docker/docker-compose.yml logs -f --tail=200

# ===== QA =====
test: ## Тесты с порогом покрытия
	$(PY) pytest -q --cov=$(PKG_DIR) --cov-fail-under=$(COV_MIN)

lint: ## Линт без автофиксов
	$(PY) ruff check .

fmt: poetry_check ## Форматирование: Black, затем Ruff --fix
	$(PY) black --check app || $(PY) black app
	$(PY) ruff check . --fix --exit-non-zero-on-fix

black: ## Black (по pyproject)
	poetry_check
	$(PY) black --check $(PKG_DIR) || $(PY) black $(PKG_DIR)

ruff: ## Ruff автофиксы (lint + imports)
	poetry_check
	$(PY) ruff check . --fix --exit-non-zero-on-fix

typecheck: ## mypy (строго, по pyproject)
	$(PY) mypy --config-file pyproject.toml

coverage: ## XML-репорт покрытия
	$(PY) pytest -q --cov=$(PKG_DIR) --cov-report=xml

qa: fmt lint typecheck test ## Полная проверка качества

precommit: ## Локальный прогон pre-commit ко всем файлам
	poetry run pre-commit run --all-files

# ===== Docker / публикация =====
build: ## Сборка образа (тег = sha)
	docker build -f docker/Dockerfile \
		--build-arg BUILD_DATE="$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
		--build-arg VCS_REF="$(COMMIT)" \
		-t $(IMAGE):$(COMMIT) .

publish: build ## Публикация образа (latest + sha)
	@if [ -z "$$GHCR_TOKEN" ]; then \
		echo "Hint: export GHCR_TOKEN=... (или используйте GITHUB_TOKEN в CI)"; \
	fi
	echo | docker login ghcr.io -u $(OWNER) --password-stdin <<< "$$GHCR_TOKEN"
	docker push $(IMAGE):$(COMMIT)
	docker tag $(IMAGE):$(COMMIT) $(IMAGE):latest
	docker push $(IMAGE):latest

# ===== Security / SBOM =====
sbom: ## SBOM для Python (CycloneDX) и файловой системы (Syft)
	$(PY) pip install --no-cache-dir cyclonedx-bom syft
	# Poetry -> CycloneDX SBOM
	$(PY) cyclonedx-bom --poetry -o sbom-python.xml --format xml
	# FS SBOM (директория проекта)
	syft dir:. -o spdx-json > sbom-container.json

trivy: ## Быстрый security scan локального образа (нужен собранный образ)
	@if ! command -v trivy >/dev/null; then echo "Install trivy first"; exit 1; fi
	trivy image --severity HIGH,CRITICAL $(IMAGE):$(COMMIT) || true

# ===== Migrations / Seed =====
migrate: ## Миграции (твой скрипт)
	$(PY) python scripts/migrate.py

seed: ## Наполнение тестовыми данными
	$(PY) python scripts/seed_contracts.py
