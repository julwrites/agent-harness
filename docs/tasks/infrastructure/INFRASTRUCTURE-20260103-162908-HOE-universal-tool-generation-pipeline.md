---
id: INFRASTRUCTURE-20260103-162908-HOE
status: completed
title: Universal Tool Generation Pipeline
priority: medium
created: 2026-01-03 16:29:08
category: infrastructure
dependencies: 
type: feature
---

# Universal Tool Generation Pipeline

## Context
Tools like `task_create` or `index_add` are the hands of the Agent. However, different agents (Claude, Gemini, generic Scripts) need these tools exposed differently. We need a system that ensures **any** agent entering the repo can "read the manual" and know exactly how to use the available tools.

## Architecture

### 1. Source of Truth (`docs/interop/tool_definitions.json`)
The central registry of capabilities. This file is part of the repo. When a user adds a new script or capability, they define it here.

### 2. The Documentation Generator (`scripts/generate_tools.py`)
This script automates the creation of the "User Manual" for the Agents.

#### Artifacts Generated:
1.  **`docs/interop/TOOLS.md`**: A human/AI-readable guide.
    *   *Purpose*: The Agent reads this file to learn what it can do.
    *   *Format*: "Tool: `task_create` | Usage: `task_create 'category' 'title'` | Description: ..."
2.  **`scripts/tools.sh`**: A shell library.
    *   *Purpose*: Provides the *implementation* for CLI-based agents so they can just run `task_create "..."` in the shell.
3.  **`.claude/skills/*`**: JSON-RPC definitions (Legacy/Specific support).

## Implementation Plan

1.  **Refactor Definitions**: Ensure `tool_definitions.json` includes the `command` field.
2.  **Schema Validation**: `scripts/generate_tools.py` must validate the JSON against a schema (checking for required fields like `name`, `description`, `command`, `risk_level`) before proceeding.
3.  **Bridge Logic**:
    *   **Shell Bridge (`scripts/tools.sh`)**: Generate Bash functions that act as **delegates** to the Python scripts (e.g., `function task_create() { python3 scripts/tasks.py create "$@"; }`). This avoids re-implementing complex logic in Bash.
    *   **AI Guide (`docs/interop/TOOLS.md`)**: Ensure the generated Markdown is optimized for LLM "System Prompt" inclusion.
4.  **Agent Instruction**: Update `AGENTS.md` to point to the generated docs.

## Acceptance Criteria
- [ ] `scripts/generate_tools.py` runs without errors.
- [ ] `docs/interop/TOOLS.md` is generated and contains clear instructions for an LLM.
- [ ] `scripts/tools.sh` allows execution of tools from a standard bash shell.
- [ ] `AGENTS.md` points the Agent to these generated docs.

