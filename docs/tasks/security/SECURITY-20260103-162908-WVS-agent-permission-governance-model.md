---
id: SECURITY-20260103-162908-WVS
status: completed
title: Agent Permission Governance Model
priority: high
created: 2026-01-03 16:29:08
category: security
dependencies: INFRASTRUCTURE-20260103-162908-HOE
type: story
---

# Agent Permission Governance Model

## Context
When an Agent enters a repository, it is an outsider. It needs to know the **Rules of Engagement** for *that specific project*. We will define a standard format for these rules so the Agent can self-regulate.

## The Policy File (`docs/security/PERMISSIONS.md`)
We will create a standardized "Policy File" that allows project owners to define what agents can do.

**Methodology**:
1.  **Read First**: The Agent's system prompt (`AGENTS.md`) will be updated to say: *"Before taking action, read `docs/security/PERMISSIONS.md` to understand your authorization level."*
2.  **Self-Correction**: The Agent checks its tools against the policy.

## The Authorization Matrix (Default Template)

| Level | Name | Description | Examples |
| :--- | :--- | :--- | :--- |
| **L0** | **Viewer** | Read-only access. | `cat`, `ls`, `grep` |
| **L1** | **Contributor** | Edit docs/tasks. | `task_create`, `write_file (docs/*)` |
| **L2** | **Developer** | Edit code. | `write_file (src/*)` |
| **L3** | **Admin** | Dangerous actions. | `git push`, `rm` |

## Implementation

### 1. Tool Metadata
Update `tool_definitions.json` to include a `risk_level` for each tool. This allows the Agent to semantically understand that `rm` is riskier than `ls`.

### 2. Prompt Engineering (`AGENTS.md`)
Update the system prompt instructions:
> **PERMISSION PROTOCOL**:
> 1. Check the `risk_level` of the tool you want to use.
> 2. Compare it to your assigned Level in `PERMISSIONS.md`.
> 3. If Risk > Level, stop and ask the user for confirmation.

### 3. Bootstrap Integration
1.  **Default Policy**: Update `scripts/bootstrap.py` to generate a default `docs/security/PERMISSIONS.md` (Level 2 default) if it doesn't exist.
2.  **Safety Hook**: Add a check in `scripts/tasks.py` (or a dedicated wrapper) that warns if an agent attempts an action above its assigned level.

## Acceptance Criteria
- [ ] `docs/security/PERMISSIONS.md` created with clear definitions.
- [ ] `tool_definitions.json` updated with `risk_level` fields.
- [ ] `scripts/bootstrap.py` automatically initializes the permission policy.
- [ ] `AGENTS.md` contains strict instructions on reading and obeying the Permission file.

