.PHONY: install
install: ## install dependencies
	uv sync --extra dev

.PHONY: lint
lint: ## lint the code
	uv run flake8 . --exclude .venv --max-line-length 120

.PHONY: test
test: ## run tests
	uv run pytest

.PHONY: run
run: ## run the backend service
	uv run uvicorn main:app --reload
