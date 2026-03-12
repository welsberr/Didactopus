.PHONY: install test lint run

install:
	python -m pip install -e .[dev]

test:
	pytest

lint:
	ruff check src tests

run:
	python -m didactopus.main --domain "programming" --goal "build real projects"
