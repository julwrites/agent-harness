#!/usr/bin/env python3
import os
import sys
import json
import ast
import argparse
import re
from fnmatch import fnmatch

# Add repo root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

from scripts.lib import io, yaml, config

# Constants
INDEX_FILE = os.path.join(REPO_ROOT, "docs", "CODE_INDEX.json")
CONFIG_FILE = os.path.join(REPO_ROOT, "harness.config.yaml")

def get_source_roots():
    conf = config.get_config(REPO_ROOT)
    # Check for code_index configuration
    if "code_index" in conf and "source_roots" in conf["code_index"]:
        return [os.path.join(REPO_ROOT, r) for r in conf["code_index"]["source_roots"]]

    # Fallback to src, lib, scripts if they exist
    defaults = []
    for d in ["src", "lib", "scripts"]:
        path = os.path.join(REPO_ROOT, d)
        if os.path.exists(path):
            defaults.append(path)

    if not defaults:
        return [REPO_ROOT]
    return defaults

def save_config(source_roots):
    conf = config.get_config(REPO_ROOT)

    # Update config object
    if "code_index" not in conf:
        conf["code_index"] = {}

    # Store relative paths
    rel_roots = [os.path.relpath(r, REPO_ROOT) for r in source_roots]
    conf["code_index"]["source_roots"] = rel_roots

    # Remove _root injected by config loader
    if "_root" in conf:
        del conf["_root"]

    yaml.SimpleYaml.save(CONFIG_FILE, conf)
    print(f"Configuration saved to {CONFIG_FILE}")

def parse_python_file(filepath):
    symbols = []
    seen_methods = set()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # If we already processed this as a method, skip
                if node in seen_methods:
                    continue
                symbols.append({
                    "name": node.name,
                    "type": "function",
                    "line": node.lineno
                })
            elif isinstance(node, ast.ClassDef):
                symbols.append({
                    "name": node.name,
                    "type": "class",
                    "line": node.lineno
                })
                # Index methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                         symbols.append({
                            "name": f"{node.name}.{item.name}",
                            "type": "method",
                            "line": item.lineno
                        })
                         seen_methods.add(item)
            elif isinstance(node, ast.Assign):
                # Global variables (heuristic)
                # Only if at top level (module body) - logic for ast.walk makes this hard
                # But typically globals are interesting anywhere if they look like constants
                # For now, we'll keep it but it might pick up locals if we aren't careful.
                # AST walk doesn't tell us parent.
                # To be safer, we should only look at tree.body for Assignments.
                pass

        # Explicitly handle top-level assignments to avoid local variables
        for node in tree.body:
            if isinstance(node, ast.Assign):
                 for target in node.targets:
                    if isinstance(target, ast.Name):
                         symbols.append({
                            "name": target.id,
                            "type": "variable",
                            "line": node.lineno
                        })

    except Exception as e:
        # Ignore parsing errors
        pass

    return symbols

def index_code(verbose=False):
    roots = get_source_roots()
    index_data = {
        "files": {},
        "symbols": {}
    }

    ignore_patterns = [".git*", "__pycache__", "*.pyc", "venv", "node_modules", ".claude", "docs"]

    for root_dir in roots:
        if verbose:
            print(f"Indexing {root_dir}...")

        for root, dirs, files in os.walk(root_dir):
            # Filtering
            dirs[:] = [d for d in dirs if not any(fnmatch(d, p) for p in ignore_patterns)]

            for file in files:
                if any(fnmatch(file, p) for p in ignore_patterns):
                    continue

                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, REPO_ROOT)

                file_entry = {
                    "path": rel_path,
                    "symbols": []
                }

                # Language detection
                if file.endswith(".py"):
                    syms = parse_python_file(filepath)
                    file_entry["symbols"] = syms

                    # Update symbol index
                    for s in syms:
                        name = s["name"]
                        if name not in index_data["symbols"]:
                            index_data["symbols"][name] = []
                        index_data["symbols"][name].append({
                            "file": rel_path,
                            "line": s["line"],
                            "type": s["type"]
                        })

                index_data["files"][rel_path] = file_entry

    # Save index
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index_data, f, indent=2)

    if verbose:
        print(f"Indexed {len(index_data['files'])} files and {len(index_data['symbols'])} symbols.")
        print(f"Index saved to {INDEX_FILE}")

def load_index():
    if not os.path.exists(INDEX_FILE):
        return {"files": {}, "symbols": {}}
    with open(INDEX_FILE, "r") as f:
        return json.load(f)

def search_symbols(query):
    idx = load_index()
    results = []

    # Case insensitive search
    q = query.lower()

    for name, locations in idx["symbols"].items():
        if q in name.lower():
            for loc in locations:
                results.append({
                    "symbol": name,
                    "file": loc["file"],
                    "line": loc["line"],
                    "type": loc["type"]
                })

    return results

def lookup_symbol(symbol):
    idx = load_index()
    if symbol in idx["symbols"]:
        return idx["symbols"][symbol]
    return []

def lookup_file(filepath):
    idx = load_index()
    # Normalize path
    if filepath.startswith("./"):
        filepath = filepath[2:]

    if filepath in idx["files"]:
        return idx["files"][filepath]

    # Try fuzzy match
    for f in idx["files"]:
        if filepath in f:
            return idx["files"][f]
    return None

def find_references(symbol):
    roots = get_source_roots()
    refs = []

    # Simple regex search
    pattern = re.compile(r'\b' + re.escape(symbol) + r'\b')

    ignore_patterns = [".git*", "__pycache__", "*.pyc", "venv", "node_modules", ".claude", "docs", "CODE_INDEX.json"]

    for root_dir in roots:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not any(fnmatch(d, p) for p in ignore_patterns)]

            for file in files:
                if any(fnmatch(file, p) for p in ignore_patterns):
                    continue

                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, REPO_ROOT)

                try:
                    with open(filepath, "r", errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if pattern.search(line):
                                refs.append({
                                    "file": rel_path,
                                    "line": i,
                                    "content": line.strip()
                                })
                except:
                    pass
    return refs

def cmd_init():
    print("Code Index Initialization")
    print("-------------------------")
    print("Enter the directories containing source code (comma separated).")
    print("Default (auto-detected): " + ", ".join([os.path.relpath(r, REPO_ROOT) for r in get_source_roots()]))

    try:
        user_input = input("Source roots: ").strip()
        if user_input:
            roots = [os.path.abspath(p.strip()) for p in user_input.split(",")]
        else:
            roots = get_source_roots()

        save_config(roots)
        index_code(verbose=True)

    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)

def cmd_index():
    index_code(verbose=False)
    print("Index updated.")

def cmd_list(output_format="text"):
    idx = load_index()
    if output_format == "json":
        print(json.dumps(idx["files"], indent=2))
        return

    print(f"Indexed Files ({len(idx['files'])})")
    print("-" * 40)
    for f in sorted(idx["files"].keys()):
        sym_count = len(idx["files"][f]["symbols"])
        print(f"{f} ({sym_count} symbols)")

def cmd_search(query, output_format="text"):
    results = search_symbols(query)
    if output_format == "json":
        print(json.dumps(results, indent=2))
        return

    print(f"Search results for '{query}':")
    for r in results:
        print(f"{r['symbol']} ({r['type']}) - {r['file']}:{r['line']}")

def cmd_lookup(target, output_format="text"):
    # Try symbol first
    sym_results = lookup_symbol(target)
    if sym_results:
        if output_format == "json":
            print(json.dumps(sym_results, indent=2))
            return
        print(f"Definition(s) for symbol '{target}':")
        for r in sym_results:
             print(f"{r['file']}:{r['line']} ({r['type']})")
        return

    # Try file
    file_result = lookup_file(target)
    if file_result:
        if output_format == "json":
            print(json.dumps(file_result, indent=2))
            return
        print(f"Symbols in {file_result['path']}:")
        for s in file_result["symbols"]:
            print(f"  {s['line']:<4} {s['type']:<10} {s['name']}")
        return

    print(f"No symbol or file found matching '{target}'")

def cmd_references(symbol, output_format="text"):
    refs = find_references(symbol)
    if output_format == "json":
        print(json.dumps(refs, indent=2))
        return

    print(f"References to '{symbol}':")
    for r in refs:
        print(f"{r['file']}:{r['line']}  {r['content']}")

def main():
    parser = argparse.ArgumentParser(description="Code structure and symbol indexer")
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    subparsers.add_parser("init", parents=[parent_parser], help="Initialize and configure")
    subparsers.add_parser("index", parents=[parent_parser], help="Re-index code")
    subparsers.add_parser("list", parents=[parent_parser], help="List indexed files")

    search_p = subparsers.add_parser("search", parents=[parent_parser], help="Fuzzy search for symbols")
    search_p.add_argument("query", help="Search query")

    lookup_p = subparsers.add_parser("lookup", parents=[parent_parser], help="Lookup symbol definition or file symbols")
    lookup_p.add_argument("target", help="Symbol name or file path")

    ref_p = subparsers.add_parser("references", parents=[parent_parser], help="Find references to a symbol")
    ref_p.add_argument("symbol", help="Symbol name")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "index":
        cmd_index()
    elif args.command == "list":
        cmd_list(args.format)
    elif args.command == "search":
        cmd_search(args.query, args.format)
    elif args.command == "lookup":
        cmd_lookup(args.target, args.format)
    elif args.command == "references":
        cmd_references(args.symbol, args.format)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
