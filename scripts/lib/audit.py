import os
import json
import datetime
from scripts.lib import io, config

def log_activity(action, args=None, agent_id=None, result="success"):
    """
    Appends a structured log entry to the agent audit log.
    """
    # Get configuration
    # Note: repo_root calculation logic copied from other scripts
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_root = os.getenv("TASKS_REPO_ROOT", os.path.dirname(script_dir))
    
    conf = config.get_config(repo_root)
    log_path = os.path.join(repo_root, conf["agents"]["audit_log"])
    
    # Ensure logs directory exists
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_id": agent_id or os.getenv("AGENT_ID", "human-or-unknown"),
        "action": action,
        "args": args or {},
        "result": result
    }
    
    # Append to JSONL file
    # We use a simple file append here. 
    # Atomic write is for full file replacement, but JSONL is append-only.
    # Standard file append is usually atomic for small writes (< 4kb) on POSIX.
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write to audit log: {e}")

def audit_log(action):
    """
    Decorator for simple function auditing.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                log_activity(action, {"args": list(args), "kwargs": kwargs}, result="success")
                return res
            except Exception as e:
                log_activity(action, {"args": list(args), "kwargs": kwargs}, result=f"error: {str(e)}")
                raise e
        return wrapper
    return decorator
