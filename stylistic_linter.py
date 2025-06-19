import re

EMOJI_PATTERN = re.compile("[\U0001F600-\U0001F64F]")
SLANG_WORDS = ["lol", "omg", "wtf", "lmao", "rofl", "btw", "imo", "noob"]
EXCESS_PUNCT_PATTERN = re.compile(r'([!?])\1{2,}')

def lint_text(text, context=""):
    issues = []
    if EMOJI_PATTERN.search(text):
        issues.append(f"{context}: Contains emoji not permitted by style guide")
    lower_text = text.lower()
    found_slang = [word for word in SLANG_WORDS if word in lower_text]
    if found_slang:
        issues.append(f"{context}: Contains slang terms ({', '.join(found_slang)})")
    if EXCESS_PUNCT_PATTERN.search(text):
        issues.append(f"{context}: Contains excessive punctuation (e.g., '!!!' or '???')")
    return issues

def lint_commit_messages(commit_list):
    results = []
    for commit in commit_list:
        msg = commit.get("message", "")
        c_hash = commit.get("hash", "")[:7]
        context = f"Commit {c_hash}"
        issues = lint_text(msg, context=context)
        results.extend(issues)
    return results

def lint_file_content(filename, content):
    issues = []
    try:
        text = content if isinstance(content, str) else content.decode('utf-8', errors='ignore')
    except:
        return issues
    issues = lint_text(text, context=f"File {filename}")
    return issues