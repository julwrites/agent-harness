#!/usr/bin/env python3
"""
Continuity System for Agent Harness.
Manages Ledgers (In-Session State) and Handoffs (Between-Session State).
"""
import os
import sys
import argparse
import json
import datetime
import re
import glob

# Determine root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
CONTINUITY_DIR = os.path.join(REPO_ROOT, "docs", "continuity")
LEDGERS_DIR = os.path.join(CONTINUITY_DIR, "ledgers")
HANDOFFS_DIR = os.path.join(CONTINUITY_DIR, "handoffs")

def ensure_dirs():
    os.makedirs(LEDGERS_DIR, exist_ok=True)
    os.makedirs(HANDOFFS_DIR, exist_ok=True)

def slugify(text):
    text = text.lower().strip()
    return re.sub(r'[^a-z0-9-]', '-', text).strip('-')

def get_latest_file(directory, prefix=""):
    """Finds the most recent markdown file in the directory."""
    pattern = os.path.join(directory, f"{prefix}*.md")
    files = glob.glob(pattern)
    if not files:
        return None
    # Sort by filename (assumes YYYY-MM-DD prefix works for sorting)
    files.sort(reverse=True)
    return files[0]

def create_entry(directory, title, content, prefix=""):
    ensure_dirs()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    slug = slugify(title) if title else "untitled"
    filename = f"{prefix}{date_str}-{slug}.md"
    filepath = os.path.join(directory, filename)

    fm = f"""---
date: {datetime.date.today().isoformat()}
title: "{title}"
created: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
type: {"ledger" if directory == LEDGERS_DIR else "handoff"}
---
"""
    full_content = fm + "\n" + content + "\n"

    with open(filepath, "w") as f:
        f.write(full_content)

    return filepath

def read_file(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="Manage Continuity (Ledgers & Handoffs)")
    subparsers = parser.add_subparsers(dest="command")

    # Ledger Commands
    ledger_parser = subparsers.add_parser("ledger", help="Manage ledgers")
    ledger_sub = ledger_parser.add_subparsers(dest="action")

    # ledger create
    l_create = ledger_sub.add_parser("create", help="Create a new ledger entry")
    l_create.add_argument("title", help="Title of the ledger entry")
    l_create.add_argument("content", help="Content of the ledger")

    # ledger read-latest
    l_read = ledger_sub.add_parser("read-latest", help="Read the latest ledger")

    # Handoff Commands
    handoff_parser = subparsers.add_parser("handoff", help="Manage handoffs")
    handoff_sub = handoff_parser.add_subparsers(dest="action")

    # handoff create
    h_create = handoff_sub.add_parser("create", help="Create a new handoff")
    h_create.add_argument("title", help="Title of the handoff")
    h_create.add_argument("content", help="Content of the handoff")

    # handoff read-latest
    h_read = handoff_sub.add_parser("read-latest", help="Read the latest handoff")

    args = parser.parse_args()

    if args.command == "ledger":
        if args.action == "create":
            path = create_entry(LEDGERS_DIR, args.title, args.content, prefix="ledger-")
            print(f"Created ledger: {path}")
        elif args.action == "read-latest":
            path = get_latest_file(LEDGERS_DIR, prefix="ledger-")
            if path:
                print(read_file(path))
            else:
                print("No ledgers found.")

    elif args.command == "handoff":
        if args.action == "create":
            path = create_entry(HANDOFFS_DIR, args.title, args.content, prefix="handoff-")
            print(f"Created handoff: {path}")
        elif args.action == "read-latest":
            path = get_latest_file(HANDOFFS_DIR, prefix="handoff-")
            if path:
                print(read_file(path))
            else:
                print("No handoffs found.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
