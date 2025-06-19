#!/bin/bash
# Setup script for scheduling Axis Thorn Security Agent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEEKLY_SCRIPT="$SCRIPT_DIR/run_weekly.sh"

echo "Axis Thorn Security Agent - Cron Setup"
echo "======================================"
echo ""

# Check if weekly script exists
if [ ! -f "$WEEKLY_SCRIPT" ]; then
    echo "Error: Weekly script not found at $WEEKLY_SCRIPT"
    exit 1
fi

# Display current crontab
echo "Current crontab entries:"
crontab -l 2>/dev/null || echo "(No existing crontab)"
echo ""

# Ask user for scheduling preference
echo "When would you like to run the weekly security scan?"
echo "1) Every Monday at 9:00 AM"
echo "2) Every Sunday at 6:00 AM"
echo "3) Every Friday at 5:00 PM"
echo "4) Custom schedule"
echo ""
read -p "Select option (1-4): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 9 * * 1"
        SCHEDULE_DESC="Every Monday at 9:00 AM"
        ;;
    2)
        CRON_SCHEDULE="0 6 * * 0"
        SCHEDULE_DESC="Every Sunday at 6:00 AM"
        ;;
    3)
        CRON_SCHEDULE="0 17 * * 5"
        SCHEDULE_DESC="Every Friday at 5:00 PM"
        ;;
    4)
        echo ""
        echo "Enter custom cron schedule (e.g., '0 9 * * 1' for Monday 9 AM):"
        read -p "> " CRON_SCHEDULE
        SCHEDULE_DESC="Custom schedule: $CRON_SCHEDULE"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

# Ask for email recipient
echo ""
read -p "Enter email address for reports (or press Enter to skip): " EMAIL

# Create cron entry
if [ -n "$EMAIL" ]; then
    CRON_ENTRY="$CRON_SCHEDULE AXIS_SECURITY_EMAIL='$EMAIL' $WEEKLY_SCRIPT"
else
    CRON_ENTRY="$CRON_SCHEDULE $WEEKLY_SCRIPT"
fi

echo ""
echo "The following cron entry will be added:"
echo "$CRON_ENTRY"
echo ""
echo "This will run the security scan: $SCHEDULE_DESC"
echo ""
read -p "Continue? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo ""
    echo "✅ Cron job added successfully!"
    echo ""
    echo "To view your crontab: crontab -l"
    echo "To remove this job: crontab -e (then delete the line)"
    echo ""
    echo "Logs will be saved to: $SCRIPT_DIR/security_agent.log"
else
    echo "Setup cancelled."
fi