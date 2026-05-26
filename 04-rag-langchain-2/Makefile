.PHONY: install run lint format test check docker-build docker-run up down

install:
	uv sync --dev

run:
	uv run python -m app

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

test:
	uv run pytest

check:
	uv run python scripts/self_check.py

docker-build:
	docker build -t telegram-llm-bot .

docker-run:
	docker run --rm --env-file .env telegram-llm-bot

up:
	docker compose up -d --build

down:
	docker compose down
