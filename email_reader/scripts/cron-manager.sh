#!/bin/bash

# Nintendo Switch 2 Monitor Cron Manager
# Alternative to using Makefile targets

set -e

# Configuration
CRON_SCHEDULE="1 8-20 * * *"
CRON_COMMAND="/Users/btillinghast/sandbox/agentic/email_reader/scripts/nintendo-monitor.sh"
CRON_JOB="$CRON_SCHEDULE $CRON_COMMAND"
CRON_COMMENT="Nintendo Switch 2 Monitor"
LOG_FILE="/tmp/nintendo_monitor.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
show_help() {
    echo "Nintendo Switch 2 Monitor Cron Manager"
    echo "====================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Install the Nintendo monitor cron job"
    echo "  stop      Remove the Nintendo monitor cron job"
    echo "  status    Show current cron jobs and log status"
    echo "  logs      View Nintendo monitor logs"
    echo "  test      Test the Nintendo monitor endpoint"
    echo "  help      Show this help message"
    echo ""
    echo "Schedule: $CRON_SCHEDULE (hourly from 8 AM to 8 PM)"
    echo "Log file: $LOG_FILE"
}

install_cron() {
    echo -e "${BLUE}Installing Nintendo monitor cron job...${NC}"
    echo "Schedule: $CRON_SCHEDULE"
    echo "Command: $CRON_COMMAND"
    echo ""
    
    # Remove any existing Nintendo monitor cron jobs and add the new one
    (crontab -l 2>/dev/null | grep -v "Nintendo Switch 2 Monitor" | grep -v "nintendo/monitor/start"; echo "$CRON_SCHEDULE $CRON_COMMAND $CRON_COMMENT") | crontab -
    
    echo -e "${GREEN}✅ Cron job installed successfully!${NC}"
    echo ""
    echo "The monitor will now run every hour from 8 AM to 8 PM."
    echo "Use '$0 status' to verify installation."
    echo "Use '$0 logs' to monitor activity."
}

remove_cron() {
    echo -e "${YELLOW}Removing Nintendo monitor cron job...${NC}"
    echo ""
    
    echo "Before removal:"
    crontab -l 2>/dev/null || echo "No cron jobs found"
    echo ""
    
    # Remove Nintendo monitor cron jobs (both by comment and by endpoint)
    crontab -l 2>/dev/null | grep -v "nintendo/monitor/start" | grep -v "Nintendo Switch 2 Monitor" | crontab - || echo "No Nintendo monitor jobs found to remove"
    
    echo "After removal:"
    crontab -l 2>/dev/null || echo "No cron jobs found"
    echo ""
    
    echo -e "${GREEN}✅ Nintendo monitor cron job removal completed!${NC}"
}

show_status() {
    echo -e "${BLUE}Current cron jobs:${NC}"
    echo "=================="
    if crontab -l 2>/dev/null; then
        echo ""
    else
        echo "No cron jobs found"
        echo ""
    fi
    
    echo -e "${BLUE}Nintendo monitor log file:${NC}"
    echo "=========================="
    if [ -f "$LOG_FILE" ]; then
        echo -e "${GREEN}📄 Log file exists: $LOG_FILE${NC}"
        echo "📊 Last 3 entries:"
        tail -3 "$LOG_FILE" 2>/dev/null || echo "No entries yet"
    else
        echo -e "${YELLOW}📭 No log file found yet${NC}"
        echo "The log will be created when the cron job first runs."
    fi
}

show_logs() {
    echo -e "${BLUE}Nintendo Switch 2 Monitor Logs${NC}"
    echo "=============================="
    
    if [ -f "$LOG_FILE" ]; then
        echo "📄 Recent entries (last 20 lines):"
        echo ""
        tail -20 "$LOG_FILE"
        echo ""
        echo -e "${BLUE}💡 Use 'tail -f $LOG_FILE' to follow logs in real-time${NC}"
    else
        echo -e "${YELLOW}📭 No log file found yet.${NC}"
        echo "The log will be created when the cron job first runs."
        echo -e "${BLUE}💡 Check that the cron job is installed with '$0 status'${NC}"
    fi
}

test_endpoint() {
    echo -e "${BLUE}Testing Nintendo monitor endpoint...${NC}"
    echo "==================================="
    
    if curl -s -X POST http://localhost:8000/nintendo/monitor/start 2>/dev/null; then
        echo ""
        echo -e "${GREEN}✅ Test successful!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Test failed${NC}"
        echo "Is the service running? Try 'make up' or 'docker-compose up -d'"
        exit 1
    fi
}

# Main script logic
case "${1:-help}" in
    start)
        install_cron
        ;;
    stop)
        remove_cron
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        test_endpoint
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 