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

def list_tasks(status=None):
    print(f"{'ID':<20} {'Status':<15} {'Title'}")
    print("-" * 60)

    for root, dirs, files in os.walk(DOCS_DIR):
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

                print(f"{t_id:<20} {t_status:<15} {t_title}")

def main():
    parser = argparse.ArgumentParser(description="Manage development tasks")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("category", choices=CATEGORIES, help="Task category")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("--desc", default="To be determined", help="Task description")

    # List
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status (pending, in_progress, completed)")

    args = parser.parse_args()

    if args.command == "create":
        create_task(args.category, args.title, args.desc)
    elif args.command == "list":
        list_tasks(args.status)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
