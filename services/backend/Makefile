.PHONY: help
help: ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## install dependencies
	uv sync --extra dev

.PHONY: lint
lint: ## lint the code
	uv run flake8 . --exclude .venv --max-line-length 120

.PHONY: test
test: ## run tests
	uv run pytest

.PHONY: docker-build
docker-build: ## build docker image (use IMAGE_TAG variable for tag)
	docker build -t web-app-demo-backend:${IMAGE_TAG} .

.PHONY: run
run: ## run the backend service
	uv run uvicorn main:app --reload
