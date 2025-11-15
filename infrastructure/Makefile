.PHONY: help lint test init plan apply destroy clean format validate bootstrap

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Terraform Infrastructure Makefile$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make init"
	@echo "  make plan"
	@echo "  make apply"

init: ## Initialize Terraform (with backend configuration)
	@echo "$(BLUE)Initializing Terraform with backend...$(NC)"
	@terraform init -backend-config=terraform.tfbackend

bootstrap: ## First-time setup of infrastructure
	@echo "$(BLUE)Running first-time setup for environment...$(NC)"
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
	@terraform apply -var-file=terraform.tfvars
	@echo ""
	@echo "$(YELLOW)Step 5: Restoring backend configuration$(NC)"
	@mv providers.tf.bak providers.tf
	@echo ""
	@echo "$(YELLOW)Step 6: Migrating state to GCS backend$(NC)"
	@terraform init -migrate-state -force-copy -backend-config=terraform.tfbackend
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
	@echo "$(BLUE)Validating Terraform configuration...$(NC)"
	@terraform validate

upgrade: ## Upgrade Terraform provider versions
	@echo "$(BLUE)Upgrading Terraform providers...$(NC)"; \
	terraform init -upgrade -backend-config=terraform.tfbackend

plan: ## Create Terraform execution plan
	@echo "$(BLUE)Creating Terraform plan...$(NC)"; \
	terraform plan -var-file=terraform.tfvars

apply: ## Apply Terraform changes
	@echo "$(YELLOW)Applying Terraform changes...$(NC)"; \
	terraform apply -var-file=terraform.tfvars

destroy: ## Destroy Terraform-managed infrastructure
	@echo "$(YELLOW)WARNING: This will destroy infrastructure...$(NC)"; \
	terraform destroy -var-file=terraform.tfvars

refresh: ## Refresh Terraform state
	@echo "$(BLUE)Refreshing Terraform state for terraform...$(NC)"; \
	terraform refresh -var-file=terraform.tfvars

show: ## Show current Terraform state
	@echo "$(BLUE)Showing Terraform state...$(NC)"
	terraform show

output: ## Show Terraform outputs
	@echo "$(BLUE)Showing Terraform outputs...$(NC)"
	terraform output
