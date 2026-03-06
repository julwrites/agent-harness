#!/usr/bin/env python3
"""
Brainstorming skill backing script.
Prompts the user with questions to refine the design before coding.
Generates a design document in docs/architecture/ or docs/features/.
Creates an Epic task via scripts/tasks.py.
"""

import os
import sys
import argparse
import re
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.tasks import create_task

DOCS_DIR = os.environ.get("TASKS_REPO_ROOT", "docs")
FEATURES_DIR = os.path.join(DOCS_DIR, "features")
ARCHITECTURE_DIR = os.path.join(DOCS_DIR, "architecture")

def sanitize_slug(text):
    slug = text.lower().replace(" ", "-")
    return re.sub(r'[^a-z0-9-]', '', slug)

def run_brainstorm(title, problem, solution, edge_cases, alternatives, doc_type):
    print("Welcome to Brainstorming Mode. Refining your design...")
    print("-" * 50)

    if not title.strip():
        print("Title is required. Exiting.")
        sys.exit(1)

    if doc_type.strip().lower() in ['a', 'architecture']:
        target_dir = ARCHITECTURE_DIR
        prefix = "ARCHITECTURE"
    else:
        target_dir = FEATURES_DIR
        prefix = "FEATURE"

    os.makedirs(target_dir, exist_ok=True)

    slug = sanitize_slug(title)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{prefix}-{timestamp}-{slug}.md"
    filepath = os.path.join(target_dir, filename)

    content = f"""# {title}

## Problem Statement
{problem}

## Proposed Solution
{solution}

## Edge Cases and Pitfalls
{edge_cases}

## Alternatives Considered
{alternatives}
"""

    with open(filepath, "w") as f:
        f.write(content)

    print(f"\nDesign document created at: {filepath}")

    print("\nCreating Epic task...")

    create_task(
        category="features",
        title=title,
        description=f"Epic for {title}. See design document at {filepath}.",
        task_type="epic",
        output_format="text"
    )

def main():
    parser = argparse.ArgumentParser(description="Brainstorming and Design Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    brainstorm_parser = subparsers.add_parser("brainstorm", help="Start a brainstorming session via CLI arguments")
    brainstorm_parser.add_argument("--title", required=True, help="The title of the feature or architectural change")
    brainstorm_parser.add_argument("--problem", required=True, help="The core problem we are trying to solve")
    brainstorm_parser.add_argument("--solution", required=True, help="The proposed solution")
    brainstorm_parser.add_argument("--edge-cases", required=True, help="The edge cases or potential pitfalls")
    brainstorm_parser.add_argument("--alternatives", required=True, help="Alternatives considered, and why they were rejected")
    brainstorm_parser.add_argument("--doc-type", choices=['f', 'a', 'feature', 'architecture'], default='f', help="Is this a feature (f) or architecture (a) document?")

    args = parser.parse_args()

    if args.command == "brainstorm":
        run_brainstorm(args.title, args.problem, args.solution, args.edge_cases, args.alternatives, args.doc_type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
