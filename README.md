# Axis Thorn Security Monitoring Agent

A modular Python agent for automated weekly security & compliance auditing, tailored for AI-powered and modern web projects.

## Features

- **Static Code Analysis**: Python (Bandit) and JavaScript (ESLint) security scanning
- **Dependency Auditing**: Vulnerability scanning for Python and Node.js dependencies
- **Git Security**: Scans commit messages and diffs for secrets, large data dumps, and potential prompt injections
- **Style Compliance**: Checks for emojis, slang, and excessive punctuation per Axis Thorn guidelines
- **Automated Reporting**: Generates markdown reports with option to email results
- **Instant Status Alerts**: On-demand security status emails with priority indicators
- **Cross-platform**: Works on macOS, Linux, and Windows

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install additional tools for full functionality:
   ```bash
   npm install -g eslint
   ```
4. (Optional) For secure password storage, ensure keyring is properly configured for your OS

## Usage

### Basic Scan
```bash
python security_agent/agent.py
```

### Scan Specific Directory
```bash
python security_agent/agent.py /path/to/project
```

### Scan with Email Report
```bash
python security_agent/agent.py --email your@email.com
```

### Configure Email (first time)
```bash
python security_agent/agent.py --setup-email
```

### Show Environment Info
```bash
python security_agent/agent.py --env-info
```

### Get Immediate Status Report
```bash
python security_agent/agent.py --status
```
This saves a status report locally in `security_reports/status_report_*.txt`

### Status Report with Email (if configured)
```bash
python security_agent/agent.py --status --email your@email.com
```

### Quick Status Check (using convenience script)
```bash
./security_agent/check_status.sh
```

### Advanced Options
```bash
python security_agent/agent.py --help
```

### Continuous Weekly Monitoring
```bash
python security_agent/agent.py --weekly
```

### Monitor Multiple Paths
```bash
python security_agent/agent.py -m /path/to/project1 -m /path/to/project2
```

## Scheduling Weekly Runs

### macOS/Linux (cron)

#### Option 1: Use the Setup Script
```bash
./security_agent/setup_cron.sh
```

#### Option 2: Manual Setup
Add to crontab (`crontab -e`):
```bash
0 9 * * 1 /path/to/security_agent/run_weekly.sh
```

#### Option 3: With Custom Email
```bash
0 9 * * 1 AXIS_SECURITY_EMAIL='your@email.com' /path/to/security_agent/run_weekly.sh
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Weekly"
4. Set action to run: `python.exe C:\path\to\security_agent\agent.py`

## Report Output

Reports are saved to `security_reports/` directory by default with timestamp:
- `security_report_2024-01-15_09-30-00.md`

## Customization

Edit the following files to customize:
- `stylistic_linter.py`: Add/remove slang words or style rules
- `git_monitor.py`: Modify regex patterns for secret detection
- `reporter.py`: Customize report format and content

## Security Notes

- Email credentials are stored locally in `email_config.json`
- Consider using app-specific passwords for email
- Reports may contain sensitive file paths - review before sharing

## Troubleshooting

If tools are not detected:
- Bandit: `pip install bandit`
- pip-audit: `pip install pip-audit`
- ESLint: `npm install -g eslint`
- Ensure tools are in PATH

For deployment recommendations based on your OS:
```bash
python security_agent/agent.py --env-info
```