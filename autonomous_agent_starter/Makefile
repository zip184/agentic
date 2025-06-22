# Makefile for managing the Dockerized application
.PHONY: help up down restart rebuild logs status

.DEFAULT_GOAL := help

# ==============================================================================
# Development Commands
# ==============================================================================

up: ## Start the application services in the background
	@echo "Starting services..."
	@docker-compose up -d

down: ## Stop the application services and remove containers
	@echo "Stopping services..."
	@docker-compose down

restart: ## Restart the application services
	@echo "Restarting services..."
	@docker-compose restart

rebuild: ## Rebuild the application and restart
	@echo "Rebuilding and restarting services..."
	@docker-compose down
	@docker-compose up -d --build

logs: ## Follow the logs for the app service
	@docker-compose logs -f app

status: ## Show the status of the running services
	@docker-compose ps


# ==============================================================================
# Help
# ==============================================================================

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) 