.PHONY: dev up down test lint black ruff migrate

dev:
	docker-compose -f docker/docker-compose-local.yml up --build

up:
	docker-compose -f docker/docker-compose.yml up -d --build

down:
	docker-compose -f docker/docker-compose.yml down

test:
	pytest tests

lint:
	ruff app

black:
	black app

ruff:
	ruff app --fix

migrate:
	python scripts/migrate.py

seed:
	python scripts/seed_contracts.py
