# Superpowers Integration: Architectural Design & Implementation Plan

## 1. Overview
This document evaluates the concepts from the `obra/superpowers` repository—a complete software development workflow for coding agents—and proposes how they can be integrated into the current Agent Harness to improve its agentic engineering capabilities. The core philosophy of `superpowers` involves rigorous workflows (like TDD, Socratic brainstorming, and subagent-driven development) mapped to specific "skills" triggered at different stages of the development lifecycle.

## 2. Evaluation of `superpowers` Workflows

The `superpowers` repository defines several core workflows. Here is an evaluation of their synergy with our Agent Harness:

### 2.1 Brainstorming & Design Validation
*   **Superpowers Concept:** Before writing code, the agent refines rough ideas through questions, explores alternatives, and presents the design in chunks for user validation.
*   **Agent Harness Synergy:** High. Currently, our harness encourages "Deep Planning Mode," but this is largely instruction-based (`AGENTS.md`). A dedicated skill to formally guide the user through a Socratic design phase and automatically generate a `docs/features/` or `docs/architecture/` document would formalize this.
*   **Recommendation:** Adopt. Introduce a `brainstorming` skill that enforces design validation before allowing code creation.

### 2.2 Git Worktrees for Isolation
*   **Superpowers Concept:** Activates after design approval. Creates an isolated workspace on a new branch, runs project setup, and verifies a clean test baseline.
*   **Agent Harness Synergy:** Medium-High. While we use standard git branching, worktrees offer cleaner isolation, especially for agents that might need to switch context or for parallel subagents.
*   **Recommendation:** Adopt partially. Instead of strict git worktrees (which can complicate simple setups), introduce a `workspace-isolation` tool/skill that ensures a clean branch, runs `scripts/quality.py verify`, and establishes a baseline before work begins.

### 2.3 Detailed Implementation Plans
*   **Superpowers Concept:** Breaks approved design into 2-5 minute bite-sized tasks with exact file paths, complete code, and verification steps.
*   **Agent Harness Synergy:** Very High. We already use `scripts/tasks.py` for task management. Generating hyper-granular sub-tasks within a broader task document, or as linked dependent tasks, directly aligns with our system.
*   **Recommendation:** Adopt. Enhance `scripts/tasks.py` (or introduce a new planning script) to auto-generate micro-tasks based on a design document, complete with verification steps.

### 2.4 Subagent-Driven Development / Parallel Execution
*   **Superpowers Concept:** Dispatches fresh subagents per task with a two-stage review (spec compliance, then code quality).
*   **Agent Harness Synergy:** High. We already have the concept of "The Hive" (`.agents/` and `scripts/comm.py`). However, orchestrating subagents is currently manual.
*   **Recommendation:** Adopt. Create an orchestrator script (`scripts/orchestrate.py`) that can read micro-tasks and dispatch them to specific agent personas (e.g., `task-agent` for planning, `library-agent` for docs, and a new `coder-agent` for execution).

### 2.5 Test-Driven Development (TDD) Enforcement
*   **Superpowers Concept:** Enforces RED-GREEN-REFACTOR. Write failing test, watch fail, write code, watch pass, commit. Deletes code written before tests.
*   **Agent Harness Synergy:** High. We have `scripts/quality.py test`, but no strict enforcement of the TDD cycle during the authoring phase.
*   **Recommendation:** Adopt. Introduce a `tdd-enforcer` skill or script that requires a failing test to be committed *before* implementation code can be merged into the active branch.

### 2.6 Requesting & Receiving Code Review
*   **Superpowers Concept:** Reviews against plan, reports issues by severity. Critical issues block progress.
*   **Agent Harness Synergy:** High. We already have a "PR Review Methodology" in `AGENTS.md`. We can formalize this with a dedicated skill that automates the pre-review checklist.
*   **Recommendation:** Adopt. Enhance the existing review methodology with an automated local review skill that checks code against the task document *before* human PR submission.

### 2.7 Finishing a Development Branch
*   **Superpowers Concept:** Verifies tests, presents options (merge/PR/keep/discard), cleans up workspace.
*   **Agent Harness Synergy:** High. We have `scripts/tasks.py update [ID] completed`, but this doesn't handle the git lifecycle.
*   **Recommendation:** Adopt. Add a `finalize` or `ship` command to our workflow that runs final quality checks, creates a PR, and closes the task simultaneously.

## 3. Proposed Implementation Plan

To integrate these concepts, we will introduce the following new components, scripts, and skills.

### Phase 1: Planning & Isolation

*   **Skill: Brainstorming (`.claude/skills/brainstorming/`)**
    *   **Purpose:** Socratic design refinement.
    *   **Script Backing:** `scripts/design.py`
    *   **Functionality:** Prompts the user with questions, generates a design document in `docs/architecture/` or `docs/features/`, and creates an Epic task via `scripts/tasks.py`.

*   **Skill: Workspace Setup (`.claude/skills/workspace/`)**
    *   **Purpose:** Ensure clean isolation before coding.
    *   **Script Backing:** `scripts/workspace.py`
    *   **Functionality:** Automates branching, runs `scripts/quality.py verify` to establish a test baseline, and ensures the environment is ready for the new task.

### Phase 2: Granular Execution & TDD

*   **Skill: Micro-Planning (`.claude/skills/micro-planning/`)**
    *   **Purpose:** Break down a feature into bite-sized tasks.
    *   **Script Backing:** Enhancement to `scripts/tasks.py` (e.g., `scripts/tasks.py breakdown [TASK_ID]`)
    *   **Functionality:** Reads a design doc and generates a series of dependent micro-tasks in the task system.

*   **Skill: TDD Enforcer (`.claude/skills/tdd/`)**
    *   **Purpose:** Enforce the RED-GREEN-REFACTOR cycle.
    *   **Script Backing:** `scripts/tdd.py`
    *   **Functionality:** A state-machine tool that the agent must call. State 1: Run test (must fail). State 2: Implement code. State 3: Run test (must pass). State 4: Refactor.

### Phase 3: Subagent Orchestration & Review

*   **Feature: Orchestrator (`scripts/orchestrator.py`)**
    *   **Purpose:** Manage parallel agent execution.
    *   **Functionality:** Reads pending micro-tasks, uses the existing "Hive" (`scripts/comm.py`) to assign tasks to subagents, and monitors their completion.

*   **Skill: Local Code Review (`.claude/skills/local-review/`)**
    *   **Purpose:** Pre-PR automated review against the spec.
    *   **Script Backing:** `scripts/review.py`
    *   **Functionality:** Compares the implemented code against the original task document/design spec, flags severity issues, and blocks the transition to `review_requested` if critical issues are found.

## 4. Next Steps

1.  Review and approve this architectural proposal.
2.  Create Feature Epics and Tasks in `docs/tasks/` for the approved phases.
3.  Begin implementation of Phase 1 (Brainstorming & Workspace Isolation).
