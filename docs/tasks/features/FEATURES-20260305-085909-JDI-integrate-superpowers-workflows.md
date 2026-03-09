---
id: FEATURES-20260305-085909-JDI
status: completed
title: Integrate Superpowers Workflows
priority: medium
created: 2026-03-05 08:59:09
dependencies:
type: epic
estimate: L
---

# Integrate Superpowers Workflows

Integrate concepts from the `obra/superpowers` repository into our Agent Harness to improve its agentic engineering capabilities. The core philosophy of `superpowers` involves rigorous workflows like TDD, Socratic brainstorming, and subagent-driven development.

See the detailed architectural document in `docs/architecture/SUPERPOWERS_INTEGRATION.md`.

## Subtasks

- [x] Implement Phase 1: Planning & Isolation (`scripts/design.py`, `scripts/workspace.py`)
- [x] Implement Phase 2: Granular Execution & TDD (`scripts/tasks.py breakdown`, `scripts/tdd.py`)
- [x] Implement Phase 3: Subagent Orchestration & Review (`scripts/orchestrator.py`, `scripts/review.py`)
- [x] Update `AGENTS.md` and `docs/tasks/GUIDE.md` to reflect new workflows.
