---
id: INFRASTRUCTURE-20260103-162908-WTS
status: completed
title: Multi-Agent Message Bus
priority: high
created: 2026-01-03 16:29:08
category: infrastructure
dependencies: 
type: story
---

# Multi-Agent Message Bus

## Context
We are establishing a **standard methodology** for multi-agent collaboration within a repository. This system must be portable and self-contained so that any agent entering a project using the Agent Harness immediately knows how to communicate.

## Architecture: "The Hive"

### 1. Directory Structure
The `.agents/` directory will serve as the root for all coordination.

```text
.agents/
├── registry/          # Active agent discovery
│   └── [agent_id].json # Metadata (Role, Capabilities, Heartbeat)
├── messages/          # Mailboxes
│   ├── public/        # Broadcasts
│   │   └── [timestamp]_[uuid].json
│   └── [agent_id]/    # Private Inboxes
│       └── [timestamp]_[uuid].json
└── lock/              # (Optional) For atomic operations if needed
```

### 2. Message Schema
All messages are JSON files stored in the recipient's directory.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "codebase_investigator",
  "to": "task_planner",
  "timestamp": "2026-01-03T16:30:00Z",
  "type": "text", 
  "content": "I have completed the analysis of the memory module.",
  "metadata": {
    "priority": "high",
    "context_ref": "docs/tasks/..."
  }
}
```

## Implementation Details

### A. The Core Logic (`scripts/comm.py`)
A python library and CLI wrapper.
*   **Atomic Writes**: Implement a Write-Replace pattern (write to `.tmp`, then `os.rename`) to prevent race conditions or partial reads.
*   `Comm.register(role: str)`: Generates session ID, writes registry file.
*   `Comm.send(to: str, content: str)`: Delivers message atomically.
*   `Comm.read(agent_id: str)`: Lists, reads, and archives messages.
*   `Comm.prune(ttl_minutes: int)`: Removes registry entries for agents that haven't updated their heartbeat.

### B. The Standard Tools
These will be added to `docs/interop/tool_definitions.json`.
1.  **`agent_send`**: Send a message.
2.  **`agent_inbox`**: Check inbox.
3.  **`agent_list`**: Discover other agents.

### C. Methodology & Config
1.  **Git Ignore**: Update `.gitignore` to exclude `.agents/` content while keeping the directory via `.keep`.
2.  **Bootstrap Integration**: Update `scripts/bootstrap.py` to:
    *   Scaffold `.agents/registry` and `.agents/messages`.
    *   Ensure `.gitignore` is correctly configured for the bus.
3.  **Agent Instructions**: Update `AGENTS.md` to include a section on **Collaboration**.

## Acceptance Criteria
- [ ] `scripts/comm.py` exists and handles file IO safely.
- [ ] `.gitignore` includes `.agents/`.
- [ ] `AGENTS.md` explicitly instructs agents on how/when to use the bus.
- [ ] `tool_definitions.json` includes the new communication tools.

