#!/usr/bin/env python3
import os
import sys
import argparse
import re
from datetime import datetime

# Determine the root directory of the repo
# Assumes this script is in scripts/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs", "tasks")
TEMPLATES_DIR = os.path.join(REPO_ROOT, "templates")

CATEGORIES = [
    "foundation",
    "infrastructure",
    "domain",
    "presentation",
    "migration",
    "features",
    "testing",
]

VALID_STATUSES = [
    "pending",
    "in_progress",
    "wip_blocked",
    "completed",
    "blocked",
    "cancelled",
    "deferred"
]

def init_docs():
    """Scaffolds the documentation directory structure."""
    print("Initializing documentation structure...")

    # Create docs/tasks/ directories
    for category in CATEGORIES:
        path = os.path.join(DOCS_DIR, category)
        os.makedirs(path, exist_ok=True)
        # Create .keep file to ensure git tracks the directory
        with open(os.path.join(path, ".keep"), "w") as f:
            pass

    # Create other doc directories
    for doc_type in ["architecture", "features"]:
        path = os.path.join(REPO_ROOT, "docs", doc_type)
        os.makedirs(path, exist_ok=True)
        readme_path = os.path.join(path, "README.md")
        if not os.path.exists(readme_path):
             with open(readme_path, "w") as f:
                f.write(f"# {doc_type.capitalize()} Documentation\n\nAdd {doc_type} documentation here.\n")

    print(f"Created directories in {os.path.join(REPO_ROOT, 'docs')}")

def get_next_id(category):
    category_dir = os.path.join(DOCS_DIR, category)
    if not os.path.exists(category_dir):
        return 1

    files = os.listdir(category_dir)
    max_id = 0
    pattern = re.compile(f"{category.upper()}-(\\d+)")

    for f in files:
        if not f.endswith(".md"):
            continue
        # Search in filename
        match = pattern.search(f.upper())
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num

    return max_id + 1

def create_task(category, title, description):
    if category not in CATEGORIES:
        print(f"Error: Category '{category}' not found. Available: {', '.join(CATEGORIES)}")
        sys.exit(1)

    next_num = get_next_id(category)
    task_id = f"{category.upper()}-{next_num:03d}"

    slug = title.lower().replace(" ", "-")
    # Sanitize slug
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    filename = f"{task_id}-{slug}.md"
    filepath = os.path.join(DOCS_DIR, category, filename)

    template_path = os.path.join(TEMPLATES_DIR, "task.md")
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            content = f.read()
    else:
        # Fallback template
        content = """# Task: {title}

## Task Information
- **Task ID**: {task_id}
- **Status**: pending
- **Priority**: medium
- **Dependencies**: None

## Task Details
{description}

---
*Created: {date}*
*Status: pending*
"""

    filled_content = content.format(
        title=title,
        task_id=task_id,
        description=description,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(filled_content)

    print(f"Created task: {filepath}")

def find_task_file(task_id):
    """Finds the file path for a given task ID."""
    task_id = task_id.upper()
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.startswith(task_id) and file.endswith(".md"):
                return os.path.join(root, file)
    return None

def show_task(task_id):
    filepath = find_task_file(task_id)
    if not filepath:
        print(f"Error: Task ID {task_id} not found.")
        sys.exit(1)

    try:
        with open(filepath, "r") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def delete_task(task_id):
    filepath = find_task_file(task_id)
    if not filepath:
        print(f"Error: Task ID {task_id} not found.")
        sys.exit(1)

    try:
        os.remove(filepath)
        print(f"Deleted task: {task_id}")
    except Exception as e:
        print(f"Error deleting file: {e}")
        sys.exit(1)

def update_task_status(task_id, new_status):
    if new_status not in VALID_STATUSES:
         print(f"Error: Invalid status '{new_status}'. Valid statuses: {', '.join(VALID_STATUSES)}")
         sys.exit(1)

    filepath = find_task_file(task_id)
    if not filepath:
        print(f"Error: Task ID {task_id} not found.")
        sys.exit(1)

    with open(filepath, "r") as f:
        content = f.read()

    # Regex to find status line: - **Status**: pending
    # Match any content after the colon until newline
    status_pattern = r"(\*\*Status\*\*: )([^\n]+)"
    if not re.search(status_pattern, content):
         print(f"Error: Could not find status field in {filepath}")
         sys.exit(1)

    new_content = re.sub(status_pattern, f"\\g<1>{new_status}", content)

    # Also update metadata footer if present
    # *Status: pending*
    footer_pattern = r"(\*Status: )([^\n\*]+)(\*)"
    new_content = re.sub(footer_pattern, f"\\g<1>{new_status}\\g<3>", new_content)

    with open(filepath, "w") as f:
        f.write(new_content)

    print(f"Updated {task_id} status to {new_status}")


def list_tasks(status=None, category=None):
    # Adjust width for ID to handle longer IDs
    print(f"{'ID':<25} {'Status':<15} {'Title'}")
    print("-" * 65)

    for root, dirs, files in os.walk(DOCS_DIR):
        # Filter by category if provided
        if category:
            rel_path = os.path.relpath(root, DOCS_DIR)
            if rel_path != category:
                continue

        for file in files:
            if not file.endswith(".md") or file in ["GUIDE.md", "README.md"]:
                continue

            path = os.path.join(root, file)
            try:
                with open(path, "r") as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue

            # Extract info
            id_match = re.search(r"\*\*Task ID\*\*: ([\w-]+)", content)
            status_match = re.search(r"\*\*Status\*\*: ([\w_]+)", content)
            title_match = re.search(r"# Task: (.+)", content)

            if id_match:
                t_id = id_match.group(1)
                t_status = status_match.group(1) if status_match else "unknown"
                t_title = title_match.group(1).strip() if title_match else "No Title"

                if status and status.lower() != t_status.lower():
                    continue

                print(f"{t_id:<25} {t_status:<15} {t_title}")

def get_context():
    """Lists tasks that are currently in progress."""
    print("Current Context (in_progress):")
    list_tasks(status="in_progress")

def main():
    parser = argparse.ArgumentParser(description="Manage development tasks")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init
    subparsers.add_parser("init", help="Initialize documentation structure")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("category", choices=CATEGORIES, help="Task category")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("--desc", default="To be determined", help="Task description")

    # List
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--category", choices=CATEGORIES, help="Filter by category")

    # Show
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("task_id", help="Task ID (e.g., FOUNDATION-001)")

    # Update
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("task_id", help="Task ID (e.g., FOUNDATION-001)")
    update_parser.add_argument("status", help=f"New status: {', '.join(VALID_STATUSES)}")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID (e.g., FOUNDATION-001)")

    # Context
    subparsers.add_parser("context", help="Show current context (in_progress tasks)")

    args = parser.parse_args()

    if args.command == "create":
        create_task(args.category, args.title, args.desc)
    elif args.command == "list":
        list_tasks(args.status, args.category)
    elif args.command == "init":
        init_docs()
    elif args.command == "show":
        show_task(args.task_id)
    elif args.command == "delete":
        delete_task(args.task_id)
    elif args.command == "update":
        update_task_status(args.task_id, args.status)
    elif args.command == "context":
        get_context()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
