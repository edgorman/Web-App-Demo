.DEFAULT_GOAL := help

.PHONY: help
help: ## Prints the list of commands available
	@awk 'BEGIN {FS = ":.*##"; printf "iac - Makefile usage:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: init
init: ## Virtual environment setup
	@echo "Initialising virtual environment from pyproject"
	@uv venv .venv --python 3.13
	@uv pip install -r pyproject.toml
	@uv pip install -e .

.PHONY: init-extras
init-extras: ## Virtual environment setup with optional extras
	@echo "Initialising virtual environment from pyproject"
	@uv venv .venv --python 3.13
	@uv pip install -r pyproject.toml --all-extras
	@uv pip install -e .

.PHONY: init-lock
init-lock: ## Virtual environment setup from uv lock
	@echo "Initialising virtual environment from pyproject"
	@uv venv .venv --python 3.13
	@uv sync
	@uv pip install -e .

.PHONY: clean
clean: ## Cleans the library
	@echo "Cleaning library"
	@$(MAKE) clean-caches

.PHONY: clean-caches
clean-caches: ## Cleans the caches in the library
	@echo "Cleaning caches"
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".*cache" -exec rm -rf {} +
	@find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: destroy
destroy: ## Destroys the library
	@echo "Destroying library"
	@$(MAKE) destroy-venv

.PHONY: destroy-venv
destroy-venv: ## Destroys the virtual environment
	@echo "Destroying virtual environment"
	@rm -rf .venv

.PHONY: lint
lint: ## Lint the code with linters
	@echo "Linting code: Running linters"
	@uv run black .
	@uv run isort .
	@uv run ruff format .

.PHONY: test
test: ## Test the code with pytest
	@echo "Testing code: Running pytest"
	@uv run pytest tests -svv
