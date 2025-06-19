#!/bin/bash
# Axis Thorn Security Agent - Weekly Scheduler
# This script runs the security agent on a weekly basis

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set Python path (adjust if needed)
PYTHON_CMD="python3"

# Default email recipient (can be overridden with environment variable)
EMAIL_RECIPIENT="${AXIS_SECURITY_EMAIL:-audit@axisthorn.com}"

# Log file location
LOG_FILE="$SCRIPT_DIR/security_agent.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Main execution
main() {
    log_message "Starting Axis Thorn Security Agent weekly scan"
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run the security agent
    if [ -n "$EMAIL_RECIPIENT" ]; then
        log_message "Running scan with email to: $EMAIL_RECIPIENT"
        $PYTHON_CMD agent.py --email "$EMAIL_RECIPIENT" 2>&1 | tee -a "$LOG_FILE"
    else
        log_message "Running scan without email (no recipient configured)"
        $PYTHON_CMD agent.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Check exit status
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_message "Security scan completed successfully"
    else
        log_message "Security scan failed with exit code: ${PIPESTATUS[0]}"
        
        # Send alert email if possible
        if [ -n "$EMAIL_RECIPIENT" ] && command -v mail >/dev/null 2>&1; then
            echo "Security scan failed. Check logs at: $LOG_FILE" | \
                mail -s "Axis Thorn Security Scan Failed" "$EMAIL_RECIPIENT"
        fi
    fi
    
    log_message "Weekly scan finished"
    echo ""
}

# Check if being sourced or executed
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi