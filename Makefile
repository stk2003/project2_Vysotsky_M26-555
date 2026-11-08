.PHONY: install run lint format build

install:
	uv sync

run:
	uv run --no-editable database

lint:
	uv run ruff check .

format:
	uv run ruff format .

build:
	uv build
