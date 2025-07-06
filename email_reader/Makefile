# Makefile for managing the Dockerized application
.PHONY: help up down restart rebuild logs status cron-start cron-stop cron-status cron-logs cron-test

.DEFAULT_GOAL := help

# Nintendo Monitor Cron Configuration
CRON_SCHEDULE = 1 8-20 * * *
CRON_COMMAND = /Users/btillinghast/sandbox/agentic/email_reader/scripts/nintendo-monitor.sh
CRON_JOB = $(CRON_SCHEDULE) $(CRON_COMMAND)
CRON_COMMENT = Nintendo Switch 2 Monitor

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
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) 