.PHONY: help lint test init plan apply destroy clean format validate bootstrap

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

# Helper to get current environment (either from ENV variable or detect from .terraform)
define get_env
$(if $(ENV),$(ENV),$(shell if [ -f .terraform/terraform.tfstate ]; then \
	grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | \
	sed 's/.*: "\(.*\)-terraform-state".*/\1/' | \
	sed 's/.*-\([^-]*\)$$/\1/'; \
fi))
endef

# Helper function to check if ENV is provided (for init/bootstrap)
define require_env
	@if [ -z "$(ENV)" ]; then \
		echo "$(RED)Error: ENV is required. Usage: make $(1) ENV=[dev|prod]$(NC)"; \
		exit 1; \
	fi
endef

# Helper function to check if ENV can be detected (for plan/apply/etc)
define require_env_detected
	@DETECTED_ENV=$$(if [ -f .terraform/terraform.tfstate ]; then \
		grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | \
		sed 's/.*: "\(.*\)-terraform-state".*/\1/' | \
		sed 's/.*-\([^-]*\)$$/\1/'; \
	fi); \
	if [ -z "$$DETECTED_ENV" ]; then \
		echo "$(RED)Error: No environment detected. Run 'make init ENV=[dev|prod]' first.$(NC)"; \
		exit 1; \
	fi
endef

help: ## Show this help message
	@echo "$(BLUE)Terraform Infrastructure Makefile$(NC)"
	@echo ""
	@DETECTED_ENV=$$(if [ -f .terraform/terraform.tfstate ]; then \
		grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | \
		sed 's/.*: "\(.*\)-terraform-state".*/\1/' | \
		sed 's/.*-\([^-]*\)$$/\1/'; \
	fi); \
	if [ -n "$$DETECTED_ENV" ]; then \
		echo "$(GREEN)Current environment: $$DETECTED_ENV$(NC)"; \
		echo ""; \
	else \
		echo "$(YELLOW)No environment detected. Run 'make init ENV=[dev|prod]' first.$(NC)"; \
		echo ""; \
	fi
	@echo "Usage: make [target] ENV=[dev|prod]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make init ENV=dev"
	@echo "  make plan"
	@echo "  make apply"

init: ## Initialize Terraform with backend configuration (ENV required)
	$(call require_env,init)
	@echo "$(BLUE)Initializing Terraform for $(ENV) environment...$(NC)"
	@terraform init -reconfigure -backend-config=config/backend/$(ENV).tfbackend

bootstrap: ## First-time setup of infrastructure (ENV required)
	$(call require_env,bootstrap)
	@echo "$(BLUE)Running first-time setup for $(ENV) environment...$(NC)"
	@echo "$(YELLOW)This will create GCS bucket and enable required APIs$(NC)"
	@echo ""
	@echo "$(YELLOW)Step 1: Cleaning up any existing backend state$(NC)"
	@rm -rf .terraform terraform.tfstate terraform.tfstate.backup
	@echo ""
	@echo "$(YELLOW)Step 2: Temporarily disabling backend configuration$(NC)"
	@TF_VERSION=$$(grep 'required_version' providers.tf | cut -d '=' -f2 | tr -d ' "'); \
	mv providers.tf providers.tf.bak && \
	echo "terraform { required_version = \"$$TF_VERSION\" }" > providers.tf
	@echo ""
	@echo "$(YELLOW)Step 3: Initializing Terraform$(NC)"
	@terraform init
	@echo ""
	@echo "$(YELLOW)Step 4: Creating backend infrastructure$(NC)"
	@terraform apply -target=module.core -var-file=config/variables/$(ENV).tfvars
	@echo ""
	@echo "$(YELLOW)Step 5: Restoring backend configuration$(NC)"
	@mv providers.tf.bak providers.tf
	@echo ""
	@echo "$(YELLOW)Step 6: Migrating state to GCS backend$(NC)"
	@terraform init -migrate-state -force-copy -backend-config=config/backend/$(ENV).tfbackend
	@echo ""
	@echo "$(YELLOW)Step 7: Cleaning up temporary files$(NC)"
	@rm -f terraform.tfstate terraform.tfstate.backup
	@echo ""
	@echo "$(GREEN)Bootstrap complete! Backend is configured and ready to use.$(NC)"
	@echo "Run 'make plan' to verify."

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

upgrade: ## Upgrade Terraform provider versions
	$(call require_env_detected)
	@DETECTED_ENV=$$(grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | sed 's/.*: "\(.*\)-terraform-state".*/\1/' | sed 's/.*-\([^-]*\)$$/\1/'); \
	echo "$(BLUE)Upgrading Terraform providers for $$DETECTED_ENV environment...$(NC)"; \
	terraform init -upgrade -backend-config=config/backend/$${DETECTED_ENV}.tfbackend

test: lint validate ## Run linting and validation tests
	@echo "$(GREEN)All tests passed!$(NC)"

plan: ## Create Terraform execution plan
	$(call require_env_detected)
	@DETECTED_ENV=$$(grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | sed 's/.*: "\(.*\)-terraform-state".*/\1/' | sed 's/.*-\([^-]*\)$$/\1/'); \
	echo "$(BLUE)Creating Terraform plan for $$DETECTED_ENV environment...$(NC)"; \
	terraform plan -var-file=config/variables/$${DETECTED_ENV}.tfvars

apply: ## Apply Terraform changes
	$(call require_env_detected)
	@DETECTED_ENV=$$(grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | sed 's/.*: "\(.*\)-terraform-state".*/\1/' | sed 's/.*-\([^-]*\)$$/\1/'); \
	echo "$(YELLOW)Applying Terraform changes for $$DETECTED_ENV environment...$(NC)"; \
	terraform apply -var-file=config/variables/$${DETECTED_ENV}.tfvars

destroy: ## Destroy Terraform-managed infrastructure
	$(call require_env_detected)
	@DETECTED_ENV=$$(grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | sed 's/.*: "\(.*\)-terraform-state".*/\1/' | sed 's/.*-\([^-]*\)$$/\1/'); \
	echo "$(YELLOW)WARNING: This will destroy infrastructure in $$DETECTED_ENV environment!$(NC)"; \
	terraform destroy -var-file=config/variables/$${DETECTED_ENV}.tfvars

refresh: ## Refresh Terraform state
	$(call require_env_detected)
	@DETECTED_ENV=$$(grep '"bucket"' .terraform/terraform.tfstate 2>/dev/null | sed 's/.*: "\(.*\)-terraform-state".*/\1/' | sed 's/.*-\([^-]*\)$$/\1/'); \
	echo "$(BLUE)Refreshing Terraform state for $$DETECTED_ENV environment...$(NC)"; \
	terraform refresh -var-file=config/variables/$${DETECTED_ENV}.tfvars

show: ## Show current Terraform state
	@echo "$(BLUE)Showing Terraform state...$(NC)"
	terraform show

output: ## Show Terraform outputs
	@echo "$(BLUE)Showing Terraform outputs...$(NC)"
	terraform output
