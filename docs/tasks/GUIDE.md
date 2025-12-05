# Task Documentation System Guide

This guide explains how to create, maintain, and update task documentation. It provides a reusable system for tracking implementation work, decisions, and progress.

## Core Philosophy
**"If it's not documented in `docs/tasks/`, it didn't happen."**

## Directory Structure
Tasks are organized by category in `docs/tasks/`:
- `foundation/`: Core architecture and setup
- `infrastructure/`: Services, adapters, platform code
- `domain/`: Business logic, use cases
- `presentation/`: UI, state management
- `features/`: End-to-end feature implementation
- `migration/`: Refactoring, upgrades
- `testing/`: Testing infrastructure

## Task Document Format

We use **YAML Frontmatter** for metadata and **Markdown** for content.

### Frontmatter (Required)
```yaml
---
id: FOUNDATION-20250521-103000   # Auto-generated Timestamp ID
status: pending                  # Current status
title: Initial Project Setup     # Task Title
priority: medium                 # high, medium, low
created: 2025-05-21 10:30:00     # Creation timestamp
category: foundation             # Category
---
```

### Status Workflow
1. `pending`: Created but not started.
2. `in_progress`: Active development.
3. `review_requested`: Implementation done, awaiting code review.
4. `verified`: Reviewed and approved.
5. `completed`: Merged and finalized.
6. `wip_blocked` / `blocked`: Development halted.
7. `cancelled` / `deferred`: Stopped or postponed.

### Content Template
```markdown
# [Task Title]

## Task Information
- **Dependencies**: [List IDs]

## Task Details
[Description of what needs to be done]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Implementation Status
### Completed Work
- ✅ Implemented X (file.py)

### Blockers
[Describe blockers if any]
```

## Tools

Use the `scripts/tasks` wrapper to manage tasks.

```bash
# Create a new task
./scripts/tasks create foundation "Task Title"

# List tasks
./scripts/tasks list

# Update status
./scripts/tasks update [TASK_ID] in_progress
./scripts/tasks update [TASK_ID] review_requested
./scripts/tasks update [TASK_ID] verified
./scripts/tasks update [TASK_ID] completed

# Migrate legacy tasks (if updating from older version)
./scripts/tasks migrate
```

## Agent Integration

Agents (Claude, etc.) use this system to track their work.
- Always check `./scripts/tasks context` before starting.
- Keep the task file updated with your progress.
- Use `review_requested` when you need human feedback.
