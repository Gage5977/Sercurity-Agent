#!/usr/bin/env python3
import argparse
import os
import sys
import time
from datetime import datetime

from environment import detect_environment, recommend_deployment
from scanner import scan_python_code, scan_node_code, scan_python_dependencies, scan_node_dependencies
from git_monitor import get_recent_commits, scan_commit_messages, scan_commit_diffs
from stylistic_linter import lint_commit_messages, lint_file_content
from reporter import generate_report, generate_markdown_report, generate_status_summary
from emailer import send_report, send_status_email, prompt_email_config, load_email_config, SMTP_SERVER, SMTP_USERNAME

# Configuration
MONITOR_PATHS = ["."]  # Paths to monitor, can be extended
ONE_WEEK = 7 * 24 * 3600

def run_full_scan(paths=None, days=7, quick=False):
    """Run comprehensive security scan across all specified paths"""
    if paths is None:
        paths = MONITOR_PATHS
    
    static_issues = []
    dep_issues = []
    commit_issues = []
    style_issues = []
    
    for path in paths:
        print(f"\nScanning path: {os.path.abspath(path)}")
        
        # Static code analysis
        if not quick:
            static_issues += scan_python_code(path)
            static_issues += scan_node_code(path)
        
        # Dependency analysis
        requirements_file = os.path.join(path, "requirements.txt")
        if os.path.exists(requirements_file):
            dep_issues += scan_python_dependencies(requirements_file)
        else:
            dep_issues += scan_python_dependencies()
        dep_issues += scan_node_dependencies(path)
        
        # Git analysis
        if os.path.exists(os.path.join(path, ".git")):
            commits = get_recent_commits(repo_path=path, days=days)
            commit_issues += scan_commit_messages(commits)
            commit_issues += scan_commit_diffs(commits, repo_path=path)
            style_issues += lint_commit_messages(commits)
        
        # Style analysis on key files
        key_files = ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"]
        for filename in key_files:
            filepath = os.path.join(path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        content = f.read()
                        issues = lint_file_content(filename, content)
                        style_issues.extend(issues)
                except:
                    pass
    
    return static_issues, dep_issues, commit_issues, style_issues

def scan_project(project_path=".", days=7):
    """Legacy scan function for compatibility"""
    print(f"🔍 Scanning project: {os.path.abspath(project_path)}")
    print(f"📅 Analyzing last {days} days of activity")
    print("-" * 50)
    
    static_issues, dep_issues, commit_issues, style_issues = run_full_scan([project_path], days)
    
    results = {
        "environment": detect_environment(),
        "python_code_issues": [i for i in static_issues if i.get("test_id")],
        "node_code_issues": [i for i in static_issues if i.get("rule")],
        "python_dependencies": [i for i in dep_issues if not i.get("module")],
        "node_dependencies": [i for i in dep_issues if i.get("module") or i.get("recommendation")],
        "commit_issues": [i for i in commit_issues if i.get("type")],
        "diff_issues": [i for i in commit_issues if i.get("detail")],
        "style_issues": style_issues
    }
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Axis Thorn Security & Compliance Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("path", nargs="?", default=".",
                       help="Path to project directory (default: current directory)")
    parser.add_argument("-d", "--days", type=int, default=7,
                       help="Number of days to analyze (default: 7)")
    parser.add_argument("-e", "--email", help="Email address to send report to")
    parser.add_argument("--setup-email", action="store_true",
                       help="Configure email settings")
    parser.add_argument("--env-info", action="store_true",
                       help="Show environment info and deployment recommendations")
    parser.add_argument("-o", "--output", default="security_reports",
                       help="Output directory for reports (default: security_reports)")
    parser.add_argument("--weekly", action="store_true",
                       help="Run in weekly monitoring mode (continuous)")
    parser.add_argument("-m", "--monitor", action="append",
                       help="Additional paths to monitor (can be used multiple times)")
    parser.add_argument("--status", action="store_true",
                       help="Send immediate status email with current security state")
    parser.add_argument("--quick", action="store_true",
                       help="Quick scan mode (skip static analysis for faster results)")
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.env_info:
        env = detect_environment()
        deployment_note = recommend_deployment(env)
        print(f"[Environment] OS = {env.get('os')} (v{env.get('os_version')}), Python = {env.get('python_version')}")
        print(f"[Environment] Node.js available: {env.get('node_installed')}, npm available: {env.get('npm_installed')}")
        print(f"[Environment] Recommended deployment: {deployment_note}")
        print("\nTool availability:")
        print(f"- Bandit (Python security): {'Yes' if env.get('bandit_installed') else 'No'}")
        print(f"- ESLint (JS linting): {'Yes' if env.get('eslint_installed') else 'No'}")
        print(f"- pip-audit (Python deps): {'Yes' if env.get('pip_audit_installed') else 'No'}")
        return
    
    if args.setup_email:
        prompt_email_config()
        return
    
    # Handle status check
    if args.status:
        print("Running quick security status check...")
        
        # Run quick scan
        results = scan_project(args.path, days=1)  # Only check last 24 hours for status
        
        # Generate status summary
        status_summary = generate_status_summary(results, args.path)
        
        # Save status report locally
        os.makedirs(args.output, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        status_file = os.path.join(args.output, f"status_report_{timestamp}.txt")
        
        with open(status_file, "w") as f:
            f.write(status_summary)
        print(f"✅ Status report saved to: {status_file}")
        
        # Try to send email if configured
        config = load_email_config()
        if config and args.email:
            recipient = args.email
            if send_status_email(status_summary, recipient, config):
                print(f"✅ Status email sent to {recipient}")
            else:
                print("⚠️  Email sending failed - report saved locally")
        elif args.email:
            print("⚠️  No email configuration found - report saved locally only")
        
        # Always print summary to console
        print("\n" + "=" * 50)
        print(status_summary)
        print("=" * 50)
        
        return
    
    # Set up monitoring paths
    monitor_paths = [args.path]
    if args.monitor:
        monitor_paths.extend(args.monitor)
    
    # Weekly monitoring mode
    if args.weekly:
        print("Starting weekly monitoring mode...")
        print(f"Monitoring paths: {', '.join(monitor_paths)}")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Run scan
                static_issues, dep_issues, commit_issues, style_issues = run_full_scan(monitor_paths, args.days)
                
                # Generate report
                report_content = generate_markdown_report(static_issues, dep_issues, commit_issues, style_issues)
                
                # Save report
                os.makedirs(args.output, exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                report_file = os.path.join(args.output, f"security_report_{timestamp}.md")
                with open(report_file, "w") as f:
                    f.write(report_content)
                
                print(f"\n✅ Report saved to: {report_file}")
                
                # Email if configured
                if SMTP_SERVER and SMTP_USERNAME:
                    recipient = args.email or "audit@axisthorn.com"
                    send_report(report_file, report_content, recipient)
                
                # Wait for next week
                print(f"\nNext scan in 7 days. Sleeping until {datetime.now().strftime('%Y-%m-%d %H:%M')}...")
                time.sleep(ONE_WEEK)
                
            except KeyboardInterrupt:
                print("\nStopping weekly monitoring.")
                break
            except Exception as e:
                print(f"\n❌ Error during scan: {e}")
                print("Retrying in 1 hour...")
                time.sleep(3600)
    
    # One-time scan mode
    else:
        try:
            results = scan_project(args.path, args.days) if not args.quick else scan_project(args.path, 1)
            
            # Generate report
            print("\n📝 Generating report...")
            report_file, report_content = generate_report(results, args.output)
            print(f"✅ Report saved to: {report_file}")
            
            # Email if requested
            if args.email:
                config = load_email_config()
                if config:
                    if send_report(report_file, report_content, args.email, config):
                        print(f"✅ Report emailed to {args.email}")
                    else:
                        print("⚠️  Email sending failed - report saved locally at: " + report_file)
                else:
                    print("⚠️  No email configuration found - report saved locally at: " + report_file)
            
            # Print summary
            print("\n" + "=" * 50)
            print("SCAN COMPLETE")
            print("=" * 50)
            
            total_issues = sum([
                len(results.get("python_code_issues", [])),
                len(results.get("node_code_issues", [])),
                len(results.get("python_dependencies", [])),
                len(results.get("node_dependencies", [])),
                len(results.get("commit_issues", [])),
                len(results.get("diff_issues", [])),
                len(results.get("style_issues", []))
            ])
            
            if total_issues == 0:
                print("✅ All security checks passed!")
            else:
                print(f"⚠️  Found {total_issues} total issues. Please review the report.")
            
        except Exception as e:
            print(f"❌ Error during scan: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()