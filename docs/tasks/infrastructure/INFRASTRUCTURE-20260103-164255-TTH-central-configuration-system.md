---
id: INFRASTRUCTURE-20260103-164255-TTH
status: completed
title: Central Configuration System
priority: high
created: 2026-01-03 16:42:55
category: infrastructure
dependencies: 
type: story
---

# Central Configuration System

## Context
Currently, project settings like Task Categories (`foundation`, `features`...), directories, and allowed statuses are hardcoded in `scripts/tasks.py`. This limits the harness's portability to other projects with different workflows.

## Objective
Introduce `harness.config.yaml` as the single source of truth for project configuration.

## Requirements

### 1. Configuration Schema (`harness.config.yaml`)
```yaml
project:
  name: "MyProject"
  root: "."

tasks:
  dir: "docs/tasks"
  categories:
    - foundation
    - backend
    - frontend
    - devops
  statuses:
    - pending
    - active
    - done

agents:
  bus_dir: ".agents"
  audit_log: "logs/audit.jsonl"
```

### 2. `scripts/lib/config.py`
*   A loader that reads `harness.config.yaml`.
*   Falls back to **Default Defaults** (current hardcoded values) if the file is missing, ensuring backward compatibility.

### 3. Refactoring
*   Update `scripts/tasks.py` to import `CATEGORIES` and `VALID_STATUSES` from `config.py`.
*   Update `scripts/bootstrap.py` to generate a default config file.

## Acceptance Criteria
- [ ] `scripts/lib/config.py` implemented.
- [ ] `scripts/tasks.py` no longer has hardcoded categories/statuses (uses config).
- [ ] Users can add a new category by editing YAML, not Python.

