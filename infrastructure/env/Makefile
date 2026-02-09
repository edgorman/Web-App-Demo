.PHONY: help init-all init-env switch

ENVIRONMENTS := $(filter-out root, $(notdir $(wildcard ../config/*)))

help: ## Shows the available commands
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

init-all: ## Initialize all environments (except root)
	@for env in $(ENVIRONMENTS); do \
		echo "Initializing environment $$env..."; \
		rm -rf .terraform; \
		terraform init -backend-config=../config/$$env/terraform.tfbackend; \
	done
	@rm -rf .terraform

init-env switch: ## Initialise a specific environment (e.g., make switch dev)
	$(eval ENV := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(ENV)" ]; then \
		echo "Error: Environment not specified."; \
		echo "Usage: make $@ [dev|prod]"; \
		exit 1; \
	fi
	@echo "Switching to environment $(ENV)..."
	@rm -rf .terraform
	@terraform init -backend-config=../config/$(ENV)/terraform.tfbackend

%:
	@:
