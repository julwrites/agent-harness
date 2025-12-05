#!/usr/bin/env python3
import os
import sys
import argparse
import re
import json
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

def parse_task_content(content, filepath=None):
    """Parses task markdown content into a dictionary."""
    id_match = re.search(r"\*\*Task ID\*\*: ([\w-]+)", content)
    status_match = re.search(r"\*\*Status\*\*: ([\w_]+)", content)
    title_match = re.search(r"# Task: (.+)", content)
    priority_match = re.search(r"\*\*Priority\*\*: ([\w]+)", content)

    task_id = id_match.group(1) if id_match else "unknown"
    status = status_match.group(1) if status_match else "unknown"
    title = title_match.group(1).strip() if title_match else "No Title"
    priority = priority_match.group(1) if priority_match else "unknown"

    return {
        "id": task_id,
        "status": status,
        "title": title,
        "priority": priority,
        "filepath": filepath,
        "content": content
    }

def create_task(category, title, description, output_format="text"):
    if category not in CATEGORIES:
        msg = f"Error: Category '{category}' not found. Available: {', '.join(CATEGORIES)}"
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
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

    if output_format == "json":
        print(json.dumps({
            "id": task_id,
            "title": title,
            "filepath": filepath,
            "status": "pending"
        }))
    else:
        print(f"Created task: {filepath}")

def find_task_file(task_id):
    """Finds the file path for a given task ID."""
    task_id = task_id.upper()
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.startswith(task_id) and file.endswith(".md"):
                return os.path.join(root, file)
    return None

def show_task(task_id, output_format="text"):
    filepath = find_task_file(task_id)
    if not filepath:
        msg = f"Error: Task ID {task_id} not found."
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        sys.exit(1)

    try:
        with open(filepath, "r") as f:
            content = f.read()

        if output_format == "json":
            task_data = parse_task_content(content, filepath)
            print(json.dumps(task_data))
        else:
            print(content)
    except Exception as e:
        msg = f"Error reading file: {e}"
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        sys.exit(1)

def delete_task(task_id, output_format="text"):
    filepath = find_task_file(task_id)
    if not filepath:
        msg = f"Error: Task ID {task_id} not found."
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        sys.exit(1)

    try:
        os.remove(filepath)
        if output_format == "json":
            print(json.dumps({"success": True, "id": task_id, "message": "Deleted task"}))
        else:
            print(f"Deleted task: {task_id}")
    except Exception as e:
        msg = f"Error deleting file: {e}"
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        sys.exit(1)

def update_task_status(task_id, new_status, output_format="text"):
    if new_status not in VALID_STATUSES:
         msg = f"Error: Invalid status '{new_status}'. Valid statuses: {', '.join(VALID_STATUSES)}"
         if output_format == "json":
            print(json.dumps({"error": msg}))
         else:
            print(msg)
         sys.exit(1)

    filepath = find_task_file(task_id)
    if not filepath:
        msg = f"Error: Task ID {task_id} not found."
        if output_format == "json":
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        sys.exit(1)

    with open(filepath, "r") as f:
        content = f.read()

    # Regex to find status line: - **Status**: pending
    # Match any content after the colon until newline
    status_pattern = r"(\*\*Status\*\*: )([^\n]+)"
    if not re.search(status_pattern, content):
         msg = f"Error: Could not find status field in {filepath}"
         if output_format == "json":
            print(json.dumps({"error": msg}))
         else:
            print(msg)
         sys.exit(1)

    new_content = re.sub(status_pattern, f"\\g<1>{new_status}", content)

    # Also update metadata footer if present
    # *Status: pending*
    footer_pattern = r"(\*Status: )([^\n\*]+)(\*)"
    new_content = re.sub(footer_pattern, f"\\g<1>{new_status}\\g<3>", new_content)

    with open(filepath, "w") as f:
        f.write(new_content)

    if output_format == "json":
        print(json.dumps({"success": True, "id": task_id, "status": new_status}))
    else:
        print(f"Updated {task_id} status to {new_status}")


def list_tasks(status=None, category=None, output_format="text"):
    tasks = []

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
                if output_format == "text":
                    print(f"Error reading {path}: {e}")
                continue

            # Parse content
            task = parse_task_content(content, path)

            # Skip files that don't look like tasks (no ID)
            if task["id"] == "unknown":
                continue

            if status and status.lower() != task["status"].lower():
                continue

            tasks.append(task)

    if output_format == "json":
        # Remove 'content' and 'filepath' for cleaner list output, or keep them?
        # User requested JSON output, usually a summary list is good.
        # But for full machine readability, maybe 'filepath' is useful.
        # I'll exclude 'content' to keep it small, include 'filepath'.
        summary = [{k: v for k, v in t.items() if k != 'content'} for t in tasks]
        print(json.dumps(summary))
    else:
        # Adjust width for ID to handle longer IDs
        print(f"{'ID':<25} {'Status':<15} {'Title'}")
        print("-" * 65)
        for t in tasks:
            print(f"{t['id']:<25} {t['status']:<15} {t['title']}")

def get_context(output_format="text"):
    """Lists tasks that are currently in progress."""
    if output_format == "text":
        print("Current Context (in_progress):")
    list_tasks(status="in_progress", output_format=output_format)

def main():
    parser = argparse.ArgumentParser(description="Manage development tasks")

    # Common argument for format
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init
    subparsers.add_parser("init", help="Initialize documentation structure")

    # Create
    create_parser = subparsers.add_parser("create", parents=[parent_parser], help="Create a new task")
    create_parser.add_argument("category", choices=CATEGORIES, help="Task category")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("--desc", default="To be determined", help="Task description")

    # List
    list_parser = subparsers.add_parser("list", parents=[parent_parser], help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--category", choices=CATEGORIES, help="Filter by category")

    # Show
    show_parser = subparsers.add_parser("show", parents=[parent_parser], help="Show task details")
    show_parser.add_argument("task_id", help="Task ID (e.g., FOUNDATION-001)")

    # Update
    update_parser = subparsers.add_parser("update", parents=[parent_parser], help="Update task status")
    update_parser.add_argument("task_id", help="Task ID (e.g., FOUNDATION-001)")
    update_parser.add_argument("status", help=f"New status: {', '.join(VALID_STATUSES)}")

    # Delete
    delete_parser = subparsers.add_parser("delete", parents=[parent_parser], help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID (e.g., FOUNDATION-001)")

    # Context
    subparsers.add_parser("context", parents=[parent_parser], help="Show current context (in_progress tasks)")

    args = parser.parse_args()

    # Default format to text if not present (e.g. init doesn't have it)
    fmt = getattr(args, "format", "text")

    if args.command == "create":
        create_task(args.category, args.title, args.desc, output_format=fmt)
    elif args.command == "list":
        list_tasks(args.status, args.category, output_format=fmt)
    elif args.command == "init":
        init_docs()
    elif args.command == "show":
        show_task(args.task_id, output_format=fmt)
    elif args.command == "delete":
        delete_task(args.task_id, output_format=fmt)
    elif args.command == "update":
        update_task_status(args.task_id, args.status, output_format=fmt)
    elif args.command == "context":
        get_context(output_format=fmt)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
