---
id: INFRASTRUCTURE-20260103-164255-PVU
status: completed
title: Atomic File I/O Library
priority: critical
created: 2026-01-03 16:42:55
category: infrastructure
dependencies: 
type: story
---

# Atomic File I/O Library

## Context
In a multi-agent environment, concurrency is guaranteed. Multiple agents (or an agent and a human) may attempt to modify `docs/tasks/` or `.agents/` files simultaneously. The current `open(..., 'w')` implementation is unsafe and will lead to race conditions and data corruption.

## Objective
Create a shared utility module `scripts/lib/io.py` that handles safe file operations.

## Requirements

### 1. `write_atomic(filepath, content)`
*   **Mechanism**:
    1.  Create a temporary file in the same directory (to ensure same filesystem).
    2.  Write content to temp file.
    3.  Flush and `os.fsync` to ensure durability.
    4.  `os.rename` (atomic POSIX operation) to overwrite the target.
*   **Retry Logic**: Optional simple backoff if the target is locked (Windows).

### 2. `read_safe(filepath)`
*   **Mechanism**: Robust reading that handles transient file locks or disappearing files (if an atomic move is in progress).

### 3. Refactoring
*   Update `scripts/tasks.py` to use `write_atomic`.
*   Update `scripts/memory.py` to use `write_atomic`.
*   Ensure the future `scripts/comm.py` uses this library.

## Acceptance Criteria
- [ ] `scripts/lib/io.py` exists and passes unit tests for concurrency.
- [ ] `scripts/tasks.py` imports and uses the library.
- [ ] No direct `open(..., 'w')` calls remain in the codebase for persistent data.

