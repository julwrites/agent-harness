#!/usr/bin/env python3
import os
import sys
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
AGENTS_FILE = os.path.join(REPO_ROOT, "AGENTS.md")
CLAUDE_FILE = os.path.join(REPO_ROOT, "CLAUDE.md")
TEMPLATE_MAINTENANCE = os.path.join(REPO_ROOT, "templates", "maintenance_mode.md")

def check_state():
    print("Repository Analysis:")
    files = [f for f in os.listdir(REPO_ROOT) if not f.startswith(".")]
    print(f"Files in root: {len(files)}")

    if os.path.exists(os.path.join(REPO_ROOT, "src")) or os.path.exists(os.path.join(REPO_ROOT, "lib")):
        print("Status: EXISTING REPOSITORY (Found src/ or lib/)")
    else:
        print("Status: NEW REPOSITORY (Likely)")

    print("\nNext Steps:")
    print("1. Run 'python3 scripts/tasks.py create foundation \"Initial Setup\"' to track your work.")
    print("2. Explore docs/architecture/ and docs/features/.")
    print("3. When ready to switch to maintenance mode, run: python3 scripts/bootstrap.py finalize")

def finalize():
    print("Finalizing setup...")
    if not os.path.exists(TEMPLATE_MAINTENANCE):
        print(f"Error: Template {TEMPLATE_MAINTENANCE} not found.")
        sys.exit(1)

    # Read template
    with open(TEMPLATE_MAINTENANCE, "r") as f:
        content = f.read()

    # Overwrite AGENTS.md
    with open(AGENTS_FILE, "w") as f:
        f.write(content)

    print(f"Updated {AGENTS_FILE} with maintenance instructions.")

    # Check CLAUDE.md symlink
    if os.path.islink(CLAUDE_FILE):
        print(f"{CLAUDE_FILE} is a symlink. Verified.")
    else:
        print(f"{CLAUDE_FILE} is NOT a symlink. Recreating it...")
        if os.path.exists(CLAUDE_FILE):
            os.remove(CLAUDE_FILE)
        os.symlink("AGENTS.md", CLAUDE_FILE)
        print("Symlink created.")

    print("\nBootstrapping Complete! The agent is now in Maintenance Mode.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    else:
        check_state()
