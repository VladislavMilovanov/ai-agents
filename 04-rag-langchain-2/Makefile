.PHONY: install run lint format

install:
	uv sync --dev

run:
	uv run python -m app

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
