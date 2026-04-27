.PHONY: install run lint test

install:
	uv sync --all-groups

run:
	uv run python -m src.main

lint:
	uv run ruff check src tests

test:
	uv run pytest tests/ -v
