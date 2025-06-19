import subprocess
import json
import os
import shutil

def scan_python_code(path="."):
    issues = []
    if shutil.which("bandit") is None:
        return issues
    try:
        result = subprocess.run(
            ["bandit", "-q", "-f", "json", "-r", path], capture_output=True, text=True
        )
        if result.stdout:
            data = json.loads(result.stdout)
            for issue in data.get("results", []):
                issues.append({
                    "file": issue.get("filename"),
                    "line": issue.get("line_number"),
                    "issue": issue.get("issue_text"),
                    "severity": issue.get("issue_severity"),
                    "confidence": issue.get("issue_confidence"),
                    "test_id": issue.get("test_id")
                })
    except Exception as e:
        print("Error running Bandit:", e)
    return issues

def scan_node_code(path="."):
    issues = []
    if shutil.which("eslint") is None:
        return issues
    try:
        result = subprocess.run(
            ["eslint", "-f", "json", "."], cwd=path, capture_output=True, text=True
        )
        if result.stdout:
            data = json.loads(result.stdout)
            for file_result in data:
                file_path = file_result.get("filePath")
                for msg in file_result.get("messages", []):
                    issues.append({
                        "file": file_path,
                        "line": msg.get("line"),
                        "message": msg.get("message"),
                        "rule": msg.get("ruleId"),
                        "severity": msg.get("severity")
                    })
    except Exception as e:
        print("ESLint error:", e)
    return issues

def scan_python_dependencies(requirements_file=None):
    vulns = []
    if shutil.which("pip-audit") is None:
        return vulns
    try:
        cmd = ["pip-audit", "-f", "json"]
        if requirements_file:
            cmd += ["-r", requirements_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout or "[]")
        for pkg in data:
            name = pkg.get("name")
            version = pkg.get("version")
            for vuln in pkg.get("vulns", []):
                vulns.append({
                    "package": name,
                    "version": version,
                    "vuln_id": vuln.get("id"),
                    "description": vuln.get("description", ""),
                    "fix_versions": vuln.get("fix_versions", [])
                })
    except Exception as e:
        print("Error running pip-audit:", e)
    return vulns

def scan_node_dependencies(path="."):
    vulns = []
    if not os.path.isfile(os.path.join(path, "package.json")):
        return vulns
    if shutil.which("npm") is None:
        return vulns
    try:
        result = subprocess.run(["npm", "audit", "--json"], cwd=path, capture_output=True, text=True)
        data = json.loads(result.stdout or "{}")
        if "advisories" in data:
            advisories = data["advisories"]
            for adv in advisories.values():
                vulns.append({
                    "package": adv.get("module_name"),
                    "version": adv.get("findings", [{}])[0].get("version", ""),
                    "vuln_id": adv.get("title", ""),
                    "severity": adv.get("severity", ""),
                    "recommendation": adv.get("recommendation")
                })
        elif "vulnerabilities" in data:
            for pkg, info in data.get("vulnerabilities", {}).items():
                vulns.append({
                    "package": pkg,
                    "version": info.get("installedVersion", ""),
                    "vuln_id": ", ".join(str(v) for v in info.get("via", [])),
                    "severity": info.get("severity", "")
                })
    except Exception as e:
        print("Error running npm audit:", e)
    return vulns