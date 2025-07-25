.PHONY: dev up down test lint black ruff migrate seed typecheck coverage build publish sbom

dev:
	docker-compose -f docker/docker-compose-local.yml up --build

up:
	docker-compose -f docker/docker-compose.yml up -d --build

down:
	docker-compose -f docker/docker-compose.yml down

test:
	pytest -q --cov=app --cov-fail-under=90

lint:
	ruff app

black:
	black app

ruff:
	ruff app --fix

typecheck:
	mypy --strict app

coverage:
	pytest -q --cov=app --cov-report=xml

build:
	docker build -f docker/Dockerfile -t ghcr.io/$(OWNER)/docuscope:$(shell git rev-parse --short HEAD) .

publish: build
	docker push ghcr.io/$(OWNER)/docuscope:$(shell git rev-parse --short HEAD)

sbom:
	pip install cyclonedx-bom syft --no-cache-dir
	cyclonedx-py -o sbom-python.xml --format xml
	syft packages dir:. -o json > sbom-container.json

migrate:
	python scripts/migrate.py

seed:
	python scripts/seed_contracts.py
