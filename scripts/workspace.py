#!/usr/bin/env python3
"""
Workspace skill backing script.
Ensures clean isolation before coding.
Automates branching and runs tests to establish a baseline.
"""

import os
import sys
import subprocess
import argparse

def setup_workspace(task_id):
    """
    Sets up the workspace for a given task ID.
    Runs `quality verify` and checks out a new branch.
    """
    print(f"Setting up workspace for task: {task_id}")
    print("-" * 50)

    # Step 1: Run quality verify to establish a test baseline
    print("Running quality verify to establish a test baseline...")

    repo_root = os.environ.get("TASKS_REPO_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    quality_script = os.path.join(repo_root, "scripts", "quality.py")

    result = subprocess.run([sys.executable, quality_script, "verify"], cwd=repo_root)

    if result.returncode != 0:
        print("\nError: `quality verify` failed. Please fix the baseline before starting a new task.", file=sys.stderr)
        sys.exit(1)

    print("\nQuality verify passed. Baseline established.")

    # Step 2: Check out a new branch
    print(f"Creating and checking out branch: {task_id}...")

    git_result = subprocess.run(["git", "checkout", "-b", task_id], cwd=repo_root)

    if git_result.returncode != 0:
        print(f"\nError: Failed to create or checkout branch '{task_id}'.", file=sys.stderr)
        sys.exit(1)

    print(f"\nWorkspace is ready. You are now on branch: {task_id}")

def main():
    parser = argparse.ArgumentParser(description="Workspace Setup Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    setup_parser = subparsers.add_parser("setup", help="Set up workspace for a new task")
    setup_parser.add_argument("task_id", help="The ID of the task to start working on")

    args = parser.parse_args()

    if args.command == "setup":
        setup_workspace(args.task_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
