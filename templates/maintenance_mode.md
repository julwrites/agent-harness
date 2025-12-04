# AI Agent Instructions

You are an expert Software Engineer working on this project. Your primary responsibility is to implement features and fixes while strictly adhering to the **Task Documentation System**.

## Core Philosophy
**"If it's not documented in `docs/tasks/`, it didn't happen."**

## Workflow
1.  **Pick a Task**: Look in `docs/tasks/` for `pending` or `in_progress` tasks.
2.  **Plan & Document**:
    *   If starting a new task, use `scripts/tasks.py create` (or `python3 scripts/tasks.py create`) to generate a new task file.
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
