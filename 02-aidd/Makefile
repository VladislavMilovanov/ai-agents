.PHONY: install run lint test docker-build docker-run docker-stop help

help:
	@echo "Доступные команды:"
	@echo "  make install       — установить зависимости (uv)"
	@echo "  make run           — запустить бота локально"
	@echo "  make lint          — проверить стиль кода (ruff)"
	@echo "  make test          — запустить тесты (pytest)"
	@echo "  make docker-build  — собрать Docker-образ"
	@echo "  make docker-run    — запустить бота через docker compose"
	@echo "  make docker-stop   — остановить контейнер"

install:
	uv sync --all-groups

run:
	uv run python -m src.main

lint:
	uv run ruff check src tests

test:
	uv run pytest tests/ -v

docker-build:
	docker compose build

docker-run:
	docker compose up -d

docker-stop:
	docker compose down
