.PHONY: help lint test format validate

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Package Terraform Makefile$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make lint"
	@echo "  make format"
	@echo "  make validate"

lint: ## Lint Terraform files with tflint
	@echo "$(BLUE)Linting Terraform files...$(NC)"
	@command -v tflint >/dev/null 2>&1 || { echo "$(YELLOW)tflint not found. Install with: curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash$(NC)"; exit 1; }
	tflint --init
	tflint --recursive

format: ## Format Terraform files
	@echo "$(BLUE)Formatting Terraform files...$(NC)"
	terraform fmt -recursive

validate: ## Validate Terraform configuration
	$(call require_env_detected)
	@echo "$(BLUE)Validating Terraform configuration...$(NC)"
	@terraform validate

test: lint validate ## Run linting and validation tests
	@echo "$(GREEN)All tests passed!$(NC)"
