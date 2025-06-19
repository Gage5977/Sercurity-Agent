from datetime import datetime
import os

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