#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import json
import shutil
from enum import Enum

# Determine the root directory of the repo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

TDD_STATE_FILE_DEFAULT = os.path.join(REPO_ROOT, ".tdd_state.json")

class TDDState(Enum):
    RED = "RED"
    GREEN = "GREEN"
    REFACTOR = "REFACTOR"

def get_state(state_file=TDD_STATE_FILE_DEFAULT):
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            data = json.load(f)
            return TDDState(data.get("state", "RED"))
    return TDDState.RED

def set_state(state, state_file=TDD_STATE_FILE_DEFAULT):
    with open(state_file, "w") as f:
         json.dump({"state": state.value}, f)

def get_git_diff():
    # Only checks unstaged/staged modified files
    result = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip().split("\n") if result.stdout else []

def run_tests():
    result = subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, "quality.py"), "test", "--format", "json"], capture_output=True, text=True)
    if not result.stdout:
       return False
    try:
        # Assuming last line is the JSON if multiple lines are printed
        lines = result.stdout.strip().split("\n")
        data = json.loads(lines[-1])
        return data.get("passed", False)
    except Exception as e:
        return False

def tdd_enforce_red(state_file=TDD_STATE_FILE_DEFAULT):
    """State 1: Red. Tests must be failing, and no implementation code should be written yet."""
    # Ensure tests are failing
    if run_tests():
        print("TDD Enforcer: RED Phase Failed - Tests are passing. You must write a failing test first.")
        modified_files = get_git_diff()
        non_test_files = [f for f in modified_files if not f.startswith("tests/") and f.endswith(".py")]

        if non_test_files:
            print(f"Warning: You have modified non-test files before writing failing tests: {', '.join(non_test_files)}")
            print("Please stash or revert these changes, write your tests, and try again.")
        return False

    print("TDD Enforcer: RED Phase Passed - Tests are failing. Proceed to GREEN phase.")
    set_state(TDDState.GREEN, state_file)
    return True

def tdd_enforce_green(state_file=TDD_STATE_FILE_DEFAULT):
    """State 2: Green. Tests must pass."""
    if not run_tests():
        print("TDD Enforcer: GREEN Phase Failed - Tests are still failing. Implement the code to make tests pass.")
        return False

    print("TDD Enforcer: GREEN Phase Passed - Tests are passing. Proceed to REFACTOR phase.")
    set_state(TDDState.REFACTOR, state_file)
    return True

def tdd_enforce_refactor(state_file=TDD_STATE_FILE_DEFAULT):
    """State 3: Refactor. Tests must still pass after refactoring."""
    if not run_tests():
        print("TDD Enforcer: REFACTOR Phase Failed - Tests are failing. Fix the code to make tests pass again.")
        return False

    print("TDD Enforcer: REFACTOR Phase Passed - Refactoring complete and tests pass. Cycle complete, back to RED phase.")
    set_state(TDDState.RED, state_file)
    return True

def main():
    parser = argparse.ArgumentParser(description="TDD Enforcer State Machine")
    parser.add_argument("command", choices=["state", "run", "reset"], help="Command to run")
    args = parser.parse_args()

    if args.command == "state":
        print(f"Current TDD State: {get_state().value}")
    elif args.command == "reset":
        set_state(TDDState.RED)
        print("TDD State reset to RED")
    elif args.command == "run":
        current_state = get_state()
        print(f"Running TDD Enforcer for state: {current_state.value}")

        if current_state == TDDState.RED:
            tdd_enforce_red()
        elif current_state == TDDState.GREEN:
            tdd_enforce_green()
        elif current_state == TDDState.REFACTOR:
            tdd_enforce_refactor()

if __name__ == "__main__":
    main()
