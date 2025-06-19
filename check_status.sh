#!/bin/bash
# Quick security status check script for Axis Thorn Security Agent
# Sends an immediate status email with current security state

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python3"

# Default email recipient (can be overridden)
EMAIL="${1:-${AXIS_SECURITY_EMAIL:-audit@axisthorn.com}}"

echo "======================================"
echo "Axis Thorn Security Status Check"
echo "======================================"
echo "Recipient: $EMAIL"
echo ""

# Run status check
cd "$SCRIPT_DIR"
$PYTHON_CMD agent.py --status --email "$EMAIL"

# Exit with appropriate code
exit $?