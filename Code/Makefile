.PHONY: install dev test lint format clean help run ingest

# Default Python
PYTHON := python

help:
	@echo "AI Study Guide - Available commands:"
	@echo ""
	@echo "  make install    - Install production dependencies"
	@echo "  make dev        - Install development dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make run        - Show CLI help"
	@echo "  make ingest     - Ingest test data folder"
	@echo ""

install:
	$(PYTHON) -m pip install .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=study_guide --cov-report=html

lint:
	$(PYTHON) -m ruff check study_guide/ tests/

format:
	$(PYTHON) -m ruff check --fix study_guide/ tests/
	$(PYTHON) -m ruff format study_guide/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

run:
	$(PYTHON) -m study_guide --help

ingest:
	$(PYTHON) -m study_guide ingest ./test_data

init-db:
	$(PYTHON) -m study_guide init

status:
	$(PYTHON) -m study_guide status
