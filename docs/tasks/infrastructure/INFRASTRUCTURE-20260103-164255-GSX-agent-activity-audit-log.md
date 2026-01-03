---
id: INFRASTRUCTURE-20260103-164255-GSX
status: completed
title: Agent Activity Audit Log
priority: medium
created: 2026-01-03 16:42:55
category: infrastructure
dependencies: INFRASTRUCTURE-20260103-164255-PVU
type: feature
---

# Agent Activity Audit Log

## Context
In a multi-agent system, debugging "who did what" is difficult. Git history shows the code changes, but not the *intent* or the *tool execution* that led to them. We need a high-level activity log.

## Objective
Implement a structured logging system that records tool usage and script execution.

## Requirements

### 1. `scripts/lib/audit.py`
*   **Logger**: A wrapper around `write_atomic` that appends to `logs/audit.jsonl`.
*   **Schema**:
    ```json
    {
      "timestamp": "2026-01-03T12:00:00Z",
      "agent_id": "gemini-pro-001",
      "tool": "task_update",
      "args": {"task_id": "TASK-123", "status": "completed"},
      "result": "success"
    }
    ```

### 2. Integration
*   Decorate core functions in `scripts/tasks.py` (like `create_task`, `update_task`) to automatically log their execution.
*   Update `scripts/comm.py` to log message sending/receiving.

### 3. Privacy
*   Ensure secrets (if any) are redacted before logging. (Currently low risk as most args are public IDs).

## Acceptance Criteria
- [ ] `logs/audit.jsonl` is created and populated when scripts run.
- [ ] Log entries are valid JSONL.
- [ ] `scripts/tasks.py` actions appear in the log.

