# image-upscaler — developer task runner
# Usage: make <target>

IMAGE ?= image-upscaler
TAG ?= dev
PY ?= python

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install the package with dev extras (editable)
	$(PY) -m pip install -e ".[dev]"

.PHONY: install-ai
install-ai: ## Install with AI (Real-ESRGAN) extras
	$(PY) -m pip install -e ".[dev,ai]"

.PHONY: format
format: ## Auto-format code with black and ruff
	$(PY) -m black src tests
	$(PY) -m ruff check --fix src tests

.PHONY: lint
lint: ## Run linters (ruff + black --check)
	$(PY) -m ruff check src tests
	$(PY) -m black --check src tests

.PHONY: typecheck
typecheck: ## Run mypy static type checks
	$(PY) -m mypy

.PHONY: test
test: ## Run the test suite with coverage
	$(PY) -m pytest

.PHONY: check
check: lint typecheck test ## Run all checks (lint, types, tests)

.PHONY: build
build: ## Build sdist and wheel
	$(PY) -m build

.PHONY: clean
clean: ## Remove build artefacts and caches
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: docker-build
docker-build: ## Build the Docker image
	docker build -t $(IMAGE):$(TAG) .

.PHONY: docker-run
docker-run: ## Run the CLI in Docker (pass ARGS="...")
	docker run --rm -v "$(PWD):/work" $(IMAGE):$(TAG) $(ARGS)

.PHONY: scan
scan: ## Run a Trivy filesystem vulnerability scan
	trivy fs --severity HIGH,CRITICAL --ignore-unfixed .

.PHONY: scan-image
scan-image: docker-build ## Build the image and Trivy-scan it
	trivy image --severity HIGH,CRITICAL --ignore-unfixed $(IMAGE):$(TAG)
