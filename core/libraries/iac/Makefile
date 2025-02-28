.PHONY: init
init: ## Virtual environment setup
	@echo "Creating virtual environment from pyproject"
	@uv venv .venv --python 3.13
	@uv pip install -r pyproject.toml

.PHONY: init-extras
init-extras: ## Virtual environment setup with optional extras
	@echo "Creating virtual environment from pyproject"
	@uv venv .venv --python 3.13
	@uv pip install -r pyproject.toml --all-extras

.PHONY: init-lock
init-lock: ## Virtual environment setup from uv lock
	@echo "Creating virtual environment from pyproject"
	@uv venv .venv --python 3.13
	@uv sync

.PHONY: test
test: ## Test the code with pytest
	@echo "Testing code: Running pytest"
	@uv run pytest tests -svv

.PHONY: lint
lint: ## Lint the code with linters
	@echo "Linting code: Running linters"
	@uv run black .
	@uv run isort .
	@uv run ruff format .

.PHONY: help
help: ## Prints the list of commands available
	@awk 'BEGIN {FS = ":.*##"; printf "iac - Makefile usage:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
