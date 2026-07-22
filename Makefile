.PHONY: install test lint check sequence-demo run

install:
	python -m pip install -e .[dev]

test:
	pytest

lint:
	ruff check src tests

check: lint test

sequence-demo:
	python -m didactopus.main sequence-plan

run:
	python -m didactopus.main --help
