---
id: FOUNDATION-20260203-EVAL-BEADS
status: pending
title: Evaluate Beads Features for Agent Harness Adoption
priority: high
created: 2026-02-03 00:30:00
category: foundation
type: task
estimate: 5
dependencies: []
---

# Evaluate Beads Features for Agent Harness Adoption

## Task Information
- **Dependencies**: None

## Context
The [Beads](https://github.com/steveyegge/beads) project represents a significant evolution in "Git-backed Graph Issue Tracking" for AI agents. `agent-harness` currently uses a file-based task system (`docs/tasks/*.md`) managed by `scripts/tasks.py`. This evaluation focuses on specific high-value features from Beads that should be adopted to evolve `agent-harness` into a robust Agentic Framework.

## Feature Analysis & Adoption Plan

### 1. Graph Data Structure & Dependencies
**Beads Approach**: Treating tasks as nodes in a standard graph (DAG). Explicit `parent <-> child` and `blocking <-> blocked_by` relationships.
**Current Harness**: Loose dependency lists (`dependencies: [ID]`) in Frontmatter.
**Improvement Proposal**:
- Move from "List of Dependencies" to Typed Relationships:
    - `depends_on`: (Blocking)
    - `part_of`: (Parent/Child)
    - `related_to`: (Context)
- **Action**: Update `scripts/tasks.py` to enforce and validate these relationships.
- **Benefit**: Better context retrieval. When an agent works on a task, it can pull in the *parent* context automatically.

### 2. Context Compaction (Memory Decay)
**Beads Approach**: "Semantic memory decay" summarizes old closed tasks to save context window.
**Current Harness**: Tasks just sit there. `archive/` folder exists but files are full size.
**Improvement Proposal**:
- Implement `scripts/tasks.py compact [TASK_ID]`.
- Uses an LLM to read a completed task (and its subtasks) and replace the content with a high-level summary, moving the full details to a simplified archive or git history.
- **Benefit**: Keeps the active "Context Window" of the project clean and small, enabling long-horizon agents to work without token overload.

### 3. Distributed ID System
**Beads Approach**: Hash-based IDs (`bd-a1b2`) derived from content/author to prevent collisions in distributed/branch-based workflows.
**Current Harness**: Timestamp-based IDs (`CATEGORY-YYYYMMDD-HHMMSS`).
**Analysis**: Timestamps are "okay" for single-user, but bad for widespread distributed teams. Hash IDs are superior for merging.
**Recommendation**:
- Stick with Timestamp IDs for now for human readability (easier to sort chronologically by eye).
- **OR**: Adopt a hybrid `YYYYMMDD-HASH` to ensure uniqueness without losing sortability.

### 4. "Auto-Ready" Task Detection
**Beads Approach**: `bd ready` shows tasks that are unblocked (dependencies met).
**Current Harness**: `scripts/tasks.py next` has a basic algorithm.
**Improvement Proposal**:
- Refine `next` logic to strictly hide tasks where `depends_on` tasks are not `completed` or `verified`.
- Add a "Ready" state or view that only shows actionable items.

## Implementation Roadmap

### Phase 1: Core Graph Enhancements
- [ ] **Data Model Update**: Update `scripts/tasks.py` to support `parent` and `related` fields in Frontmatter.
- [ ] **Visualization**: Add `scripts/tasks.py graph` to output Mermaid/DOT graph of the task network.

### Phase 2: Context Management
- [ ] **Compaction Script**: Create `scripts/compact.py` (or add to `tasks.py`) to summarize verified tasks.

### Phase 3: Developer Experience
- [ ] **CLI Polish**: Alias `./scripts/tasks.py` to `tasks` or `ah` (AgentHarness) for ergonomics.

## Acceptance Criteria
- [ ] Roadmap approved by user.
- [ ] Implementation tasks created for Phase 1.
