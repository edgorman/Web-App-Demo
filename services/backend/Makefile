.PHONY: help
help: ## show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## install dependencies
	go mod download

.PHONY: lint
lint: ## lint the code
	@unformatted=$$(gofmt -l .); \
	if [ -n "$$unformatted" ]; then \
		echo "gofmt needed for:"; echo "$$unformatted"; exit 1; \
	fi
	go vet ./...

.PHONY: format
format: ## format the code
	gofmt -w .

.PHONY: test
test: ## run tests
	go test ./...

.PHONY: docker-build
docker-build: ## build docker image (use IMAGE_TAG variable for tag)
	docker build -t web-app-demo-backend:${IMAGE_TAG} .

.PHONY: run
run: ## run the backend service
	go run . run
