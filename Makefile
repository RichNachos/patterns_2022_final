.PHONY: help
.DEFAULT_GOAL := help

install: ## Install requirements
	pip install -r requirements.txt

format: ## Run code formatters
	isort tests core infra runner
	black tests core infra runner

lint: ## Run code linters
	isort --check tests core infra runner
	black --check tests core infra runner
	flake8 tests core infra runner
	mypy tests core infra runner

clean: ## Run formatters and linters | NO TESTS
	isort tests core infra runner
	black tests core infra runner
	isort --check tests core infra runner
	black --check tests core infra runner
	flake8 tests core infra runner
	mypy tests core infra runner

test:  ## Run tests with coverage
	pytest --cov

all:   ## run formatters, linters and tests
	isort tests core infra runner
	black tests core infra runner
	isort --check tests core infra runner
	black --check tests core infra runner
	flake8 tests core infra runner
	mypy tests core infra runner
	pytest --cov

run:   ## Run program
	python3.10 runner/__main__.py
