.PHONY: ingest ingest-test clean lint format test ci docker-build docker-run docker-up help

# Default target
help:
	@echo "NCR Property Price Estimation - Makefile"
	@echo "========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make ingest          - Run full scraper (all cities)"
	@echo "  make ingest-test     - Test scraper (Noida, 10 pages)"
	@echo "  make ingest-gurgaon  - Scrape only Gurgaon"
	@echo "  make lint            - Run ruff linter + format check"
	@echo "  make format          - Auto-fix lint + formatting"
	@echo "  make test            - Run pytest suite"
	@echo "  make ci              - Run lint then test (same as CI)"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-run      - Run Docker container on port 8000"
	@echo "  make docker-up       - Start via docker-compose"
	@echo "  make clean           - Remove output files"
	@echo ""

# ---- Data Ingestion ----

ingest:
	python ncr_property_price_estimation/data/ingest.py

ingest-test:
	python ncr_property_price_estimation/data/ingest.py --city noida --max-pages 10

ingest-gurgaon:
	python ncr_property_price_estimation/data/ingest.py --city gurgaon

ingest-noida:
	python ncr_property_price_estimation/data/ingest.py --city noida

ingest-delhi:
	python ncr_property_price_estimation/data/ingest.py --city delhi

# ---- Code Quality ----

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

# ---- Testing ----

test:
	pytest

# ---- CI (mirrors GitHub Actions) ----

ci: lint test

# ---- Cleanup ----

clean:
	rm -f data/raw/magicbricks_production.parquet
	rm -f data/raw/checkpoint_production.json
	@echo "Cleaned output files"

# ---- Docker ----

docker-build:
	docker build -t ncr-property-api:latest .

docker-run: docker-build
	docker run --rm -p 8000:8000 ncr-property-api:latest

docker-up:
	docker compose up --build

