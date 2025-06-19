import platform
import shutil
import subprocess

def detect_environment():
    env_info = {}
    env_info["os"] = platform.system()
    env_info["os_version"] = platform.release()
    env_info["python_version"] = platform.python_version()
    env_info["node_installed"] = shutil.which("node") is not None
    env_info["npm_installed"] = shutil.which("npm") is not None
    env_info["pip_installed"] = shutil.which("pip") is not None or shutil.which("pip3") is not None
    env_info["bandit_installed"] = shutil.which("bandit") is not None
    env_info["eslint_installed"] = shutil.which("eslint") is not None
    env_info["pip_audit_installed"] = shutil.which("pip-audit") is not None
    return env_info

def recommend_deployment(env_info):
    os_name = env_info.get("os", "")
    if os_name in ["Linux", "Darwin"]:
        if os_name == "Linux" and shutil.which("systemctl"):
            return "Run as a systemd service for continuous monitoring"
        else:
            return "Schedule weekly via cron (e.g., @weekly in crontab)"
    elif os_name == "Windows":
        return "Use Task Scheduler for weekly run, or install as a Windows Service (via NSSM)"
    return "CLI (manual or scheduled invocation)"

if __name__ == "__main__":
    env = detect_environment()
    print("Environment detected:", env)
    print("Deployment suggestion:", recommend_deployment(env))