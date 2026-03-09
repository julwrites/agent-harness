#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

from scripts import tasks
from scripts.lib import io

def check_task(task_id, mock_failure=False, output_format="text"):
    """
    Performs a pre-PR automated review against the spec.
    Returns True if passed, False if critical issues found.
    """
    filepath = tasks.find_task_file(task_id)
    if not filepath:
        msg = f"Error: Task ID {task_id} not found."
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return False

    content = io.read_text(filepath)

    # Mock finding critical issues if mock_failure is true or CRITICAL_ISSUE is in the file
    if mock_failure or "CRITICAL_ISSUE" in content:
        msg = f"Critical Issue: The implementation of {task_id} does not match the spec."
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return False

    msg = f"Success: No critical issues found for {task_id}."
    if output_format == "json":
        print(json.dumps({"success": msg}))
    else:
        print(msg)
    return True

def main():
    parser = argparse.ArgumentParser(description="Local Code Review")
    subparsers = parser.add_subparsers(dest="command")

    # Check
    check_parser = subparsers.add_parser("check", help="Perform automated review against the spec")
    check_parser.add_argument("--task-id", required=True, help="The ID of the task to review")
    check_parser.add_argument("--mock-failure", action="store_true", help="Mock a critical issue")
    check_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    if args.command == "check":
        if check_task(args.task_id, mock_failure=args.mock_failure, output_format=args.format):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
