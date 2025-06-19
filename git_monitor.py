from datetime import datetime, timedelta
import subprocess
import re

PROMPT_INJECTION_REGEX = re.compile(r'(?i)ignore\s+.*instructions')
SENSITIVE_REGEX = re.compile(r'(api[_-]?key|secret[_-]?key|password)\s*[:=]\s*[^\s]+', re.IGNORECASE)

def get_recent_commits(repo_path=".", days=7):
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        log_output = subprocess.check_output(
            ["git", "-C", repo_path, "log", f'--since="{since_date}"', "--pretty=format:%H%n%B%n---END---"],
            text=True
        )
    except Exception as e:
        print("Git log failed:", e)
        return []
    commits = []
    entries = log_output.split("---END---")
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        lines = entry.splitlines()
        commit_hash = lines[0] if lines else ""
        message = "\n".join(lines[1:]).strip()
        commits.append({"hash": commit_hash, "message": message})
    return commits

def scan_commit_messages(commits):
    issues = []
    for commit in commits:
        msg = commit.get("message", "")
        c_hash = commit.get("hash")
        if PROMPT_INJECTION_REGEX.search(msg):
            issues.append({
                "commit": c_hash,
                "type": "Prompt Injection Phrase",
                "excerpt": msg[:100] + ("..." if len(msg) > 100 else "")
            })
        if SENSITIVE_REGEX.search(msg):
            issues.append({
                "commit": c_hash,
                "type": "Sensitive Info in Commit Message",
                "excerpt": msg[:100] + ("..." if len(msg) > 100 else "")
            })
    return issues

def scan_commit_diffs(commits, repo_path="."):
    issues = []
    for commit in commits:
        commit_hash = commit.get("hash")
        if not commit_hash:
            continue
        try:
            diff_text = subprocess.check_output(
                ["git", "-C", repo_path, "show", commit_hash, "--pretty=", "--unified=0"],
                text=True, errors='ignore'
            )
        except Exception as e:
            continue
        if "PRIVATE KEY" in diff_text or re.search(r"AKIA[0-9A-Z]{16}", diff_text):
            issues.append({
                "commit": commit_hash,
                "type": "Potential Secret in Diff",
                "detail": "Diff contains text that looks like a secret (e.g. private key or AWS key)."
            })
        if diff_text.count("\n") > 500:
            issues.append({
                "commit": commit_hash,
                "type": "Large commit",
                "detail": "Commit adds a large amount of data; review for accidental data leak."
            })
    return issues