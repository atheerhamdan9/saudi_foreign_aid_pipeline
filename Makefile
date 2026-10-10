
.PHONY: install run test lint clean

install:
	python -m pip install -e ".[dev]"

run:
	python -m pipeline.cli

test:
	python -m pytest

lint:
	ruff check .

clean:
	rm -rf .pytest_cache .ruff_cache