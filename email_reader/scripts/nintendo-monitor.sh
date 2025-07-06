#!/bin/bash
# Nintendo Switch 2 Monitor - Comprehensive Monitoring Script
# Author: Nintendo Alert System
# Description: Monitors for Nintendo Switch 2 announcements with detailed logging

# Configuration
LOG_FILE="/tmp/nintendo_monitor.log"
SERVICE_URL="http://localhost:8000/nintendo/monitor/start"
CONNECT_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=5

# Colors for output (if running manually)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log with timestamp
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Function to check if service is running
check_service_health() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [INFO] Checking service health..." >> "$LOG_FILE"
    
    if curl -s --fail --connect-timeout 10 http://localhost:8000/nintendo/monitor/status > /dev/null 2>&1; then
        echo "[$timestamp] [SUCCESS] Service is healthy and responsive" >> "$LOG_FILE"
        return 0
    else
        echo "[$timestamp] [WARNING] Service health check failed" >> "$LOG_FILE"
        return 1
    fi
}

# Function to run monitor with retries
run_monitor() {
    local attempt=1
    local success=false
    
    while [ $attempt -le $MAX_RETRIES ] && [ "$success" = false ]; do
        log_message "INFO" "Starting Nintendo monitor check (attempt $attempt/$MAX_RETRIES)..."
        
        # Run the monitor command
        if curl -s --fail --show-error --connect-timeout "$CONNECT_TIMEOUT" -X POST "$SERVICE_URL" >> "$LOG_FILE" 2>&1; then
            log_message "SUCCESS" "Nintendo monitor completed successfully"
            success=true
            return 0
        else
            local exit_code=$?
            log_message "ERROR" "Nintendo monitor failed with exit code: $exit_code"
            
            case $exit_code in
                6)
                    log_message "ERROR" "DNS resolution failed - check network connectivity"
                    ;;
                7)
                    log_message "ERROR" "Connection refused - service may be down"
                    log_message "INFO" "Checking if Docker containers are running..."
                    if command -v docker >/dev/null 2>&1; then
                        docker ps --format "table {{.Names}}\t{{.Status}}" | grep email_reader >> "$LOG_FILE" 2>&1 || log_message "INFO" "No email_reader containers found"
                    fi
                    ;;
                28)
                    log_message "ERROR" "Connection timeout after ${CONNECT_TIMEOUT}s - service may be overloaded"
                    ;;
                *)
                    log_message "ERROR" "Unknown error occurred"
                    ;;
            esac
            
            if [ $attempt -lt $MAX_RETRIES ]; then
                log_message "INFO" "Retrying in ${RETRY_DELAY}s..."
                sleep $RETRY_DELAY
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_message "CRITICAL" "All $MAX_RETRIES attempts failed - Nintendo monitoring is DOWN"
    return 1
}

# Function to check system prerequisites
check_prerequisites() {
    log_message "INFO" "Checking system prerequisites..."
    
    # Check if curl is available
    if ! command -v curl >/dev/null 2>&1; then
        log_message "ERROR" "curl is not installed or not in PATH"
        return 1
    fi
    
    # Check if log directory is writable
    if ! touch "$LOG_FILE" 2>/dev/null; then
        log_message "ERROR" "Cannot write to log file: $LOG_FILE"
        return 1
    fi
    
    # Check network connectivity
    if ! ping -c 1 localhost >/dev/null 2>&1; then
        log_message "WARNING" "localhost ping failed - network issues detected"
    fi
    
    log_message "INFO" "Prerequisites check completed"
    return 0
}

# Function to display usage
show_usage() {
    echo "Nintendo Switch 2 Monitor - Comprehensive Monitoring Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -v, --verbose        Enable verbose output"
    echo "  -t, --test           Run in test mode (no retries)"
    echo "  --check-health       Only check service health"
    echo "  --show-logs          Show recent log entries"
    echo ""
    echo "Examples:"
    echo "  $0                   Run normal monitoring"
    echo "  $0 --verbose         Run with verbose output"
    echo "  $0 --show-logs       Show recent logs"
    echo ""
    echo "Log file: $LOG_FILE"
}

# Function to show recent logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "=== Recent Nintendo Monitor Logs ==="
        tail -20 "$LOG_FILE"
    else
        echo "No log file found at: $LOG_FILE"
    fi
}

# Main execution
main() {
    local verbose=false
    local test_mode=false
    local health_check_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -t|--test)
                test_mode=true
                MAX_RETRIES=1
                shift
                ;;
            --check-health)
                health_check_only=true
                shift
                ;;
            --show-logs)
                show_logs
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Start monitoring
    log_message "INFO" "=== Nintendo Switch 2 Monitor Starting ==="
    log_message "INFO" "Script version: 1.0"
    log_message "INFO" "Service URL: $SERVICE_URL"
    log_message "INFO" "Connect timeout: ${CONNECT_TIMEOUT}s"
    log_message "INFO" "Max retries: $MAX_RETRIES"
    
    if [ "$verbose" = true ]; then
        echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] Starting Nintendo Switch 2 monitoring...${NC}"
    fi
    
    # Check prerequisites
    if ! check_prerequisites; then
        log_message "CRITICAL" "Prerequisites check failed - aborting"
        exit 1
    fi
    
    # Health check only mode
    if [ "$health_check_only" = true ]; then
        if check_service_health; then
            log_message "INFO" "Health check completed successfully"
            exit 0
        else
            log_message "ERROR" "Health check failed"
            exit 1
        fi
    fi
    
    # Run the monitor
    if run_monitor; then
        log_message "INFO" "=== Nintendo Switch 2 Monitor Completed Successfully ==="
        if [ "$verbose" = true ]; then
            echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] Nintendo monitoring completed successfully${NC}"
        fi
        exit 0
    else
        log_message "CRITICAL" "=== Nintendo Switch 2 Monitor Failed ==="
        if [ "$verbose" = true ]; then
            echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] Nintendo monitoring failed${NC}"
        fi
        exit 1
    fi
}

# Run main function with all arguments
main "$@" 