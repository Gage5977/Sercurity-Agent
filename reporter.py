from datetime import datetime
import os
import socket

def generate_markdown_report(static_issues, dep_vulns, commit_issues, style_issues):
    lines = []
    lines.append(f"# Weekly Security and Compliance Report\n")
    lines.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    lines.append("## 1. Static Code Vulnerabilities")
    if static_issues:
        lines.append("| File/Location | Issue/Description | Severity |")
        lines.append("| ------------- | ----------------- | -------- |")
        for issue in static_issues:
            loc = issue.get("file", "unknown")
            if issue.get("line"):
                loc += f":{issue['line']}"
            desc = issue.get("issue") or issue.get("message") or ""
            sev = issue.get("severity", "N/A")
            if issue.get("test_id"):
                desc = f"[{issue['test_id']}] " + desc
            elif issue.get("rule"):
                desc = f"[{issue['rule']}] " + desc
            lines.append(f"| {loc} | {desc} | {sev} |")
    else:
        lines.append("_No static code security issues found in this period._")
    lines.append("")
    lines.append("## 2. Dependency Vulnerabilities")
    if dep_vulns:
        lines.append("| Package | Version | Vulnerability/ID | Severity | Fix Available |")
        lines.append("| ------- | ------- | ---------------- | -------- | ------------- |")
        for vuln in dep_vulns:
            name = vuln.get("package") or vuln.get("module")
            version = vuln.get("version", vuln.get("current_version", ""))
            vid = vuln.get("vuln_id", vuln.get("title", ""))
            sev = vuln.get("severity", vuln.get("severity", ""))
            fix = "Yes" if vuln.get("fix_versions") or vuln.get("recommendation") else "No"
            lines.append(f"| {name} | {version} | {vid} | {sev or 'N/A'} | {fix} |")
    else:
        lines.append("_No known vulnerable dependencies found._")
    lines.append("")
    lines.append("## 3. AI/Prompt Injection & Sensitive Findings")
    if commit_issues:
        for issue in commit_issues:
            if issue.get("commit"):
                c = issue['commit'][:7]
                issue_type = issue.get("type", "Issue")
                detail = issue.get("detail") or issue.get("excerpt") or ""
                lines.append(f"- **Commit {c}** – {issue_type}: {detail}")
            else:
                lines.append(f"- {issue}")
    else:
        lines.append("_No prompt-injection or sensitive-data issues detected in commits._")
    lines.append("")
    lines.append("## 4. Stylistic Compliance Issues")
    if style_issues:
        for issue in style_issues:
            lines.append(f"- {issue}")
    else:
        lines.append("_No stylistic violations found (commit messages and code are clean)._")
    lines.append("")
    lines.append("---")
    lines.append("*End of Report*")
    return "\n".join(lines)

def generate_report(scan_results, output_dir="security_reports"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data for enhanced report format
    static_issues = scan_results.get("python_code_issues", []) + scan_results.get("node_code_issues", [])
    dep_vulns = scan_results.get("python_dependencies", []) + scan_results.get("node_dependencies", [])
    commit_issues = scan_results.get("commit_issues", []) + scan_results.get("diff_issues", [])
    style_issues = scan_results.get("style_issues", [])
    
    # Generate enhanced markdown report
    report_content = generate_markdown_report(static_issues, dep_vulns, commit_issues, style_issues)
    
    # Write report
    report_file = os.path.join(output_dir, f"security_report_{timestamp}.md")
    
    with open(report_file, "w") as f:
        f.write(report_content)
    
    return report_file, report_content

def generate_status_summary(scan_results, project_path="."):
    """Generate a concise status summary for email"""
    lines = []
    
    # Header
    hostname = socket.gethostname()
    lines.append(f"Security Status Report - {hostname}")
    lines.append(f"Project: {os.path.abspath(project_path)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("\n" + "=" * 50 + "\n")
    
    # Quick summary
    static_issues = scan_results.get("python_code_issues", []) + scan_results.get("node_code_issues", [])
    dep_vulns = scan_results.get("python_dependencies", []) + scan_results.get("node_dependencies", [])
    commit_issues = scan_results.get("commit_issues", []) + scan_results.get("diff_issues", [])
    style_issues = scan_results.get("style_issues", [])
    
    total_issues = len(static_issues) + len(dep_vulns) + len(commit_issues) + len(style_issues)
    
    # Status indicator
    if total_issues == 0:
        status = "✅ SECURE - All checks passed"
        priority = "Normal"
    elif total_issues < 5:
        status = "⚠️ WARNING - Minor issues detected"
        priority = "Medium"
    elif total_issues < 20:
        status = "🔶 ATTENTION - Multiple issues found"
        priority = "High"
    else:
        status = "❌ CRITICAL - Immediate attention required"
        priority = "Critical"
    
    lines.append(f"Overall Status: {status}")
    lines.append(f"Priority Level: {priority}")
    lines.append(f"Total Issues: {total_issues}")
    
    # Breakdown
    lines.append("\nIssue Breakdown:")
    lines.append(f"- Code Security Issues: {len(static_issues)}")
    lines.append(f"- Dependency Vulnerabilities: {len(dep_vulns)}")
    lines.append(f"- Git/Commit Issues: {len(commit_issues)}")
    lines.append(f"- Style Violations: {len(style_issues)}")
    
    # Critical findings
    critical_items = []
    
    # Check for high severity vulnerabilities
    for vuln in dep_vulns:
        if vuln.get("severity", "").upper() in ["HIGH", "CRITICAL"]:
            critical_items.append(f"- {vuln['package']}: {vuln.get('severity')} severity vulnerability")
    
    # Check for secrets in commits
    for issue in commit_issues:
        if "secret" in issue.get("type", "").lower() or "password" in issue.get("type", "").lower():
            critical_items.append(f"- Potential secret in commit {issue['commit'][:7]}")
    
    if critical_items:
        lines.append("\n🚨 Critical Findings:")
        lines.extend(critical_items[:5])  # Limit to 5
        if len(critical_items) > 5:
            lines.append(f"... and {len(critical_items) - 5} more")
    
    # Recent activity
    if "environment" in scan_results:
        env = scan_results["environment"]
        lines.append("\nEnvironment:")
        lines.append(f"- OS: {env.get('os')} {env.get('os_version')}")
        lines.append(f"- Python: {env.get('python_version')}")
        lines.append(f"- Security Tools: Bandit={'Yes' if env.get('bandit_installed') else 'No'}, "
                    f"pip-audit={'Yes' if env.get('pip_audit_installed') else 'No'}")
    
    # Recommendations
    lines.append("\nRecommended Actions:")
    if dep_vulns:
        lines.append("1. Update vulnerable dependencies immediately")
    if static_issues:
        lines.append("2. Review and fix code security issues")
    if commit_issues:
        lines.append("3. Audit recent commits for sensitive data")
    if total_issues == 0:
        lines.append("1. Continue regular security monitoring")
        lines.append("2. Keep dependencies up to date")
    
    lines.append("\n" + "=" * 50)
    lines.append("\nFor detailed report, run: python3 agent.py --email <your-email>")
    
    return "\n".join(lines)