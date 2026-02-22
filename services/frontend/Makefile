.PHONY: help
help: ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## install dependencies
	npm install

.PHONY: dev
dev: ## start development server
	npm run dev

.PHONY: build
build: ## build for production
	npm run build

.PHONY: preview
preview: ## preview production build
	npm run preview

.PHONY: lint
lint: ## run linter
	npm run lint

.PHONY: format
format: ## format code
	npm run format

.PHONY: clean
clean: ## clean build artifacts and dependencies
	rm -rf node_modules dist
