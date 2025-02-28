.PHONY: init
init: ## Install the virtual environment
	@echo "Creating virtual environment using uv"
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
