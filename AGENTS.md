# AI Agent Bootstrap Instructions

**CURRENT STATUS: BOOTSTRAPPING MODE**

You are an expert Software Architect and Project Manager. Your current goal is to bootstrap this repository for AI-driven development using a structured Task Documentation System.

## Step 1: Detect Repository State
Analyze the current directory to determine if this is a **New** or **Existing** repository.
- Run `ls -R` (excluding `.git`).
- **New Repository**: Contains only this `AGENTS.md`, `CLAUDE.md`, `LICENSE`, and the `docs/` directory provided by the template.
- **Existing Repository**: Contains other source code files, configuration files, or directories.

## Step 2: Execution Strategy

### Scenario A: New Repository
1.  **Interview**: Ask the user what they want to build. specific questions about technology stack, features, and goals.
2.  **Plan**: Propose a high-level architecture and a list of initial features.
3.  **Scaffold Documentation**:
    *   Create `docs/architecture/README.md` (Architecture Overview).
    *   Create `docs/features/README.md` (Feature List).
    *   Create `docs/tasks/README.md` (Task System Overview).
4.  **Scaffold Project**: Generate a `.gitignore` suitable for the chosen stack.
5.  **Proceed to Step 3 (Finalize).**

### Scenario B: Existing Repository
1.  **Analyze**: Read the code to understand the current architecture, features, and state.
    *   **DO NOT DELETE ANY EXISTING CODE.**
2.  **Document**:
    *   Create/Update `docs/architecture/README.md` reflecting the *current* architecture.
    *   Create/Update `docs/features/README.md` listing implemented features.
    *   Create `docs/tasks/README.md` if missing.
3.  **Identify Tasks**:
    *   If you find TODOs, bugs, or clear refactoring needs, create initial task documents in `docs/tasks/` (e.g., `docs/tasks/migration/MIGRATION-001-fix-todos.md`).
4.  **Interview**: Ask the user what their immediate goals are for this repository.
5.  **Proceed to Step 3 (Finalize).**

## Step 3: Finalize & Switch to Maintenance Mode
Once the documentation structure is in place and the user's goals are captured:

1.  **Replace** the content of this `AGENTS.md` file with the **Project Specific Instructions** template below.
2.  **Ensure** `CLAUDE.md` has the exact same content as the new `AGENTS.md`.
3.  **Notify** the user that bootstrapping is complete and the agent is ready for development tasks.

---

## [TEMPLATE] Project Specific Instructions

*(Copy the content below this line when finalizing to replace the current file)*

# AI Agent Instructions

You are an expert Software Engineer working on this project. Your primary responsibility is to implement features and fixes while strictly adhering to the **Task Documentation System**.

## Core Philosophy
**"If it's not documented in `docs/tasks/`, it didn't happen."**

## Workflow
1.  **Pick a Task**: Look in `docs/tasks/` for `pending` or `in_progress` tasks.
2.  **Plan & Document**:
    *   If starting a new task, create a new file in the appropriate `docs/tasks/` subdirectory using the template in `docs/tasks/GUIDE.md`.
    *   Update the task status to `in_progress`.
3.  **Implement**: Write code, run tests.
4.  **Update Documentation Loop**:
    *   As you complete sub-tasks, check them off in the task document.
    *   If you hit a blocker, update status to `wip_blocked` and describe the issue.
    *   Record key architectural decisions in the task document.
5.  **Finalize**:
    *   Update status to `completed`.
    *   Record actual effort.
    *   Ensure all acceptance criteria are met.

## Documentation Reference
*   **Guide**: Read `docs/tasks/GUIDE.md` for strict formatting and process rules.
*   **Architecture**: Refer to `docs/architecture/` for system design.
*   **Features**: Refer to `docs/features/` for feature specifications.

## Code Style & Standards
*   Follow the existing patterns in the codebase.
*   Ensure all new code is covered by tests (if testing infrastructure exists).
