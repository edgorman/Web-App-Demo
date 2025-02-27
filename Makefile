help: ## Prints the list of commands available
	@awk 'BEGIN {FS = ":.*##"; printf "Web-App-Demo - Makefile usage:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
