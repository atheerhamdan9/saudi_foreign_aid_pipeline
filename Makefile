.PHONY: install run test lint clean

RUN_DATE ?= $(shell date +%F)

install:
	python -m pip install -e ".[dev]"

run:
	python -m pipeline.cli run --date $(RUN_DATE)

test:
	python -m pytest

lint:
	ruff check src tests

clean:
	rm -rf .pytest_cache .ruff_cache
