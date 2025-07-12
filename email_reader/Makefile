# Makefile for managing the Dockerized application
.PHONY: help auth-gmail auth-status auth-clean up down restart rebuild logs logs-all logs-failed status cron-start cron-stop cron-status cron-logs cron-test

.DEFAULT_GOAL := help

# Nintendo Monitor Cron Configuration
CRON_SCHEDULE = 1 8-20 * * *
CRON_COMMAND = /Users/btillinghast/sandbox/agentic/email_reader/scripts/nintendo-monitor.sh
CRON_JOB = $(CRON_SCHEDULE) $(CRON_COMMAND)
CRON_COMMENT = Nintendo Switch 2 Monitor

# ==============================================================================
# Gmail Authentication
# ==============================================================================

auth-gmail: ## Run Gmail authentication setup (creates token.pickle)
	@echo "🔐 Starting Gmail authentication..."
	@echo "⚠️  This must be run locally (not in Docker) with a browser available"
	@echo ""
	@if [ ! -f "credentials.json" ]; then \
		echo "❌ ERROR: credentials.json not found!"; \
		echo ""; \
		echo "📋 Setup steps:"; \
		echo "1. Go to Google Cloud Console: https://console.cloud.google.com/"; \
		echo "2. Create/select a project"; \
		echo "3. Enable Gmail API"; \
		echo "4. Create OAuth 2.0 credentials"; \
		echo "5. Download the JSON file"; \
		echo "6. Rename it to 'credentials.json'"; \
		echo "7. Place it in this directory"; \
		echo "8. Run 'make auth-gmail' again"; \
		echo ""; \
		exit 1; \
	fi
	@python3 authenticate_gmail.py
	@echo ""
	@echo "✅ Gmail authentication completed!"
	@echo "🔄 Rebuilding containers with new credentials..."
	@make rebuild

auth-status: ## Check Gmail authentication status
	@echo "🔍 Checking Gmail authentication status..."
	@echo "======================================="
	@if [ -f "token.pickle" ]; then \
		echo "✅ token.pickle found - Gmail authentication is set up"; \
		echo "📅 File created: $$(stat -f %Sc token.pickle)"; \
	else \
		echo "❌ token.pickle not found - Gmail authentication needed"; \
		echo "💡 Run 'make auth-gmail' to set up authentication"; \
	fi
	@echo ""
	@if [ -f "credentials.json" ]; then \
		echo "✅ credentials.json found"; \
	else \
		echo "❌ credentials.json not found"; \
		echo "💡 Download from Google Cloud Console and rename to credentials.json"; \
	fi

auth-clean: ## Remove authentication files (for re-authentication)
	@echo "🧹 Cleaning authentication files..."
	@if [ -f "token.pickle" ]; then \
		rm token.pickle; \
		echo "✅ Removed token.pickle"; \
	else \
		echo "ℹ️  token.pickle not found"; \
	fi
	@echo "💡 Run 'make auth-gmail' to re-authenticate"

# ==============================================================================
# Development Commands
# ==============================================================================

up: ## Start the application services in the background
	@echo "Starting services..."
	@docker-compose up -d
	@echo ""
	@echo "Checking container status..."
	@sleep 3
	@docker-compose ps
	@echo ""
	@echo "Checking for failed containers..."
	@failed_containers=$$(docker-compose ps --filter "status=exited" --format "table {{.Name}}\t{{.Status}}" | grep -v "NAME" | grep -v "^$$" || true); \
	if [ -n "$$failed_containers" ]; then \
		echo "❌ Some containers failed to start:"; \
		echo "$$failed_containers"; \
		echo ""; \
		echo "📋 Container logs for failed services:"; \
		echo "====================================="; \
		for container in $$(docker-compose ps --filter "status=exited" --format "{{.Name}}" | grep -v "^$$"); do \
			echo ""; \
			echo "🔍 Logs for $$container:"; \
			echo "------------------------"; \
			docker logs $$container --tail 20; \
			echo ""; \
		done; \
		echo "💡 Use 'make logs' to follow app logs or 'docker logs <container-name>' for specific container logs"; \
		exit 1; \
	else \
		echo "✅ All services started successfully!"; \
		echo ""; \
		echo "🌐 Available endpoints:"; \
		echo "  - API: http://localhost:8000"; \
		echo "  - ChromaDB: http://localhost:8001"; \
		echo ""; \
		echo "📋 Use 'make logs' to follow application logs"; \
	fi

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

logs-all: ## Show logs from all services
	@docker-compose logs --tail 50

logs-failed: ## Show logs from failed containers
	@echo "Checking for failed containers..."
	@failed_containers=$$(docker-compose ps --filter "status=exited" --format "{{.Name}}" | grep -v "^$$"); \
	if [ -n "$$failed_containers" ]; then \
		echo "📋 Logs from failed containers:"; \
		echo "==============================="; \
		for container in $$failed_containers; do \
			echo ""; \
			echo "🔍 Logs for $$container:"; \
			echo "------------------------"; \
			docker logs $$container --tail 30; \
			echo ""; \
		done; \
	else \
		echo "✅ No failed containers found"; \
	fi

status: ## Show the status of the running services
	@echo "Container Status:"
	@echo "================"
	@docker-compose ps
	@echo ""
	@echo "Failed containers (if any):"
	@echo "==========================="
	@failed_containers=$$(docker-compose ps --filter "status=exited" --format "{{.Name}}" | grep -v "^$$"); \
	if [ -n "$$failed_containers" ]; then \
		echo "❌ Failed containers found:"; \
		for container in $$failed_containers; do \
			echo "  - $$container"; \
		done; \
		echo ""; \
		echo "💡 Use 'make logs' or 'docker logs <container-name>' to check logs"; \
		echo "💡 Use 'make up' to restart all services"; \
	else \
		echo "✅ No failed containers"; \
	fi


# ==============================================================================
# Nintendo Monitor Cron Management
# ==============================================================================

cron-start: ## Install Nintendo monitor cron job (runs hourly 8 AM - 8 PM)
	@echo "Installing Nintendo monitor cron job..."
	@echo "Schedule: $(CRON_SCHEDULE)"
	@echo "Command: $(CRON_COMMAND)"
	@(crontab -l 2>/dev/null | grep -v "Nintendo Switch 2 Monitor" | grep -v "nintendo/monitor/start"; echo "$(CRON_SCHEDULE) $(CRON_COMMAND) $(CRON_COMMENT)") | crontab -
	@echo "✅ Cron job installed successfully!"
	@echo "Run 'make cron-status' to verify installation"

cron-stop: ## Remove Nintendo monitor cron job
	@echo "Removing Nintendo monitor cron job..."
	@echo "Before removal:"
	@crontab -l 2>/dev/null || echo "No cron jobs found"
	@echo ""
	@crontab -l 2>/dev/null | grep -v "nintendo/monitor/start" | grep -v "Nintendo Switch 2 Monitor" | crontab - || echo "No Nintendo monitor jobs found to remove"
	@echo ""
	@echo "After removal:"
	@crontab -l 2>/dev/null || echo "No cron jobs found"
	@echo "✅ Nintendo monitor cron job removal completed!"

cron-status: ## Show current cron jobs
	@echo "Current cron jobs:"
	@echo "=================="
	@crontab -l 2>/dev/null || echo "No cron jobs found"
	@echo ""
	@echo "Nintendo monitor log file:"
	@echo "=========================="
	@if [ -f /tmp/nintendo_monitor.log ]; then \
		echo "📄 Log file exists: /tmp/nintendo_monitor.log"; \
		echo "📊 Last 3 entries:"; \
		tail -3 /tmp/nintendo_monitor.log 2>/dev/null || echo "No entries yet"; \
	else \
		echo "📭 No log file found yet"; \
	fi

cron-logs: ## View Nintendo monitor cron logs
	@echo "Nintendo Switch 2 Monitor Logs"
	@echo "=============================="
	@if [ -f /tmp/nintendo_monitor.log ]; then \
		echo "📄 Recent entries (last 20 lines):"; \
		echo ""; \
		tail -20 /tmp/nintendo_monitor.log; \
		echo ""; \
		echo "💡 Use 'tail -f /tmp/nintendo_monitor.log' to follow logs in real-time"; \
	else \
		echo "📭 No log file found yet. The log will be created when the cron job first runs."; \
		echo "💡 Check that the cron job is installed with 'make cron-status'"; \
	fi

cron-test: ## Test the Nintendo monitor endpoint manually
	@echo "Testing Nintendo monitor endpoint..."
	@echo "==================================="
	@curl -X POST http://localhost:8000/nintendo/monitor/start 2>/dev/null && echo "\n✅ Test successful!" || echo "\n❌ Test failed - is the service running? Try 'make up'"


# ==============================================================================
# Help
# ==============================================================================

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "📧 Gmail Authentication:"
	@awk 'BEGIN {FS = ":.*?## "} /^auth-[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🐳 Docker Services:"
	@awk 'BEGIN {FS = ":.*?## "} /^(up|down|restart|rebuild|logs|status):.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "📊 Logging & Debug:"
	@awk 'BEGIN {FS = ":.*?## "} /^logs-[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "⏰ Cron Management:"
	@awk 'BEGIN {FS = ":.*?## "} /^cron-[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "❓ Help:"
	@awk 'BEGIN {FS = ":.*?## "} /^help:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) 