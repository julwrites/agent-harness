#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import subprocess
import json
import re

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

from scripts.lib import io

# Configuration for linters
LINTERS = {
    "flake8": ["flake8", "."],
    "pylint": ["pylint", "--recursive=y", "."],
    # Add more as needed (e.g., black, mypy)
}

def check_linter_availability(linter_cmd):
    """Check if a linter is installed and available."""
    try:
        subprocess.check_call([linter_cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False

def run_tests(pattern=None, verbose=False, output_format="text"):
    """Runs tests using unittest."""
    cmd = [sys.executable, "-m", "unittest"]

    if pattern:
        # If pattern looks like a file path, convert to module notation
        if pattern.endswith(".py"):
            pattern = pattern.replace("/", ".").replace(".py", "")
        if pattern.startswith("."):
            pattern = pattern[1:]

        cmd.append(pattern)
    else:
        cmd.extend(["discover", "tests"])

    if verbose:
        cmd.append("-v")

    print(f"Running tests: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse basic results for JSON output if requested
        if output_format == "json":
            # Very basic parsing of unittest output
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            print(json.dumps({
                "passed": passed,
                "output": output,
                "command": " ".join(cmd)
            }))
        else:
            print(result.stdout)
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        msg = f"Error running tests: {e}"
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return False

def run_validation(output_format="text"):
    """Runs task validation script."""
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, "tasks.py"), "validate", "--format", "json"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            if output_format == "text":
                print("Task Validation Failed:")
                try:
                    data = json.loads(result.stdout)
                    for err in data.get("errors", []):
                        print(f" - {err}")
                except:
                    print(result.stdout)
            else:
                 print(result.stdout) # It's already JSON
            return False

        if output_format == "text":
            print("Task Validation: PASSED")
        return True

    except Exception as e:
        if output_format == "text":
             print(f"Error running validation: {e}")
        return False

def run_lint(files=None, output_format="text"):
    """Runs available linters."""

    found_any = False
    all_passed = True

    for name, cmd_template in LINTERS.items():
        base_cmd = cmd_template[0]
        if check_linter_availability(base_cmd):
            found_any = True
            cmd = list(cmd_template)

            if files:
                # Replace "." or default target with specific files
                # This is naive; assumes last arg is target
                cmd.pop()
                cmd.extend(files)

            print(f"Running {name}...")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    all_passed = False
                    print(f"[{name}] Issues found:")
                    print(result.stdout)
                    print(result.stderr)
                else:
                    print(f"[{name}] Passed.")
            except Exception as e:
                print(f"Error executing {name}: {e}")
                all_passed = False

    if not found_any:
        print("No linters found. (flake8, pylint).")
        print("Tip: Install them via pip if you want linting.")
        # We don't fail verify if linters aren't installed, but we warn
        return True

    return all_passed

def scaffold_test(src_file, output_format="text"):
    """Creates a corresponding test file for a source file."""
    if not os.path.exists(src_file):
        print(f"Error: Source file {src_file} not found.")
        return

    # Determine test path
    # src/lib/utils.py -> tests/lib/test_utils.py
    # or src/utils.py -> tests/test_utils.py

    rel_path = os.path.relpath(src_file, REPO_ROOT)
    parts = rel_path.split(os.sep)

    # Handle 'src' prefix removal if common
    if parts[0] == "src":
        parts = parts[1:]
    elif parts[0] == "scripts":
        # Scripts are often tested too
        pass

    filename = parts[-1]
    dir_parts = parts[:-1]

    test_filename = f"test_{filename}"
    test_dir = os.path.join(REPO_ROOT, "tests", *dir_parts)
    test_path = os.path.join(test_dir, test_filename)

    if os.path.exists(test_path):
        print(f"Test file already exists: {test_path}")
        return

    os.makedirs(test_dir, exist_ok=True)

    # Generate import path
    # scripts/lib/utils.py -> scripts.lib.utils
    module_path = rel_path.replace(".py", "").replace(os.sep, ".")

    content = f"""import unittest
import sys
import os

# Add repo root to path for imports
# This traverses up from the test location to the repo root
# Adjust if you move this file
test_file_path = os.path.abspath(__file__)
repo_root = test_file_path
for _ in range({len(dir_parts) + 2}): # +2 for tests/ and test file itself
    repo_root = os.path.dirname(repo_root)

if repo_root not in sys.path:
    sys.path.append(repo_root)

from {module_path} import *

class Test{filename.replace('.py', '').capitalize()}(unittest.TestCase):
    def setUp(self):
        pass

    def test_example(self):
        # TODO: Implement tests for {module_path}
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""

    io.write_atomic(test_path, content)
    print(f"Created test scaffold: {test_path}")

def cmd_verify(output_format="text"):
    """Runs all checks required for a 'safe' commit."""
    print("--- Quality Verification ---\n")

    print("1. Task Validation")
    valid_tasks = run_validation(output_format)
    print("")

    print("2. Unit Tests")
    valid_tests = run_tests(verbose=False, output_format=output_format)
    print("")

    # Optional: Linting
    # print("3. Linting")
    # valid_lint = run_lint(output_format=output_format)

    if valid_tasks and valid_tests:
        print("\n✅ Verification PASSED")
        sys.exit(0)
    else:
        print("\n❌ Verification FAILED")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Quality Control Tool")
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Verify
    subparsers.add_parser("verify", parents=[parent_parser], help="Run full verification suite (Tests + Task Validation)")

    # Test
    test_parser = subparsers.add_parser("test", parents=[parent_parser], help="Run unit tests")
    test_parser.add_argument("pattern", nargs="?", help="Specific test pattern or file")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Lint
    lint_parser = subparsers.add_parser("lint", parents=[parent_parser], help="Run linters")
    lint_parser.add_argument("files", nargs="*", help="Specific files to lint")

    # Scaffold
    scaffold_parser = subparsers.add_parser("map", parents=[parent_parser], help="Create a test file for a source file")
    scaffold_parser.add_argument("src_file", help="Source file path")

    args = parser.parse_args()

    if args.command == "verify":
        cmd_verify(args.format)
    elif args.command == "test":
        run_tests(args.pattern, args.verbose, args.format)
    elif args.command == "lint":
        run_lint(args.files, args.format)
    elif args.command == "map":
        scaffold_test(args.src_file, args.format)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
