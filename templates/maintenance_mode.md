# AI Agent Instructions

You are an expert Software Engineer working on this project. Your primary responsibility is to implement features and fixes while strictly adhering to the **Task Documentation System**.

## Core Philosophy
**"If it's not documented in `docs/tasks/`, it didn't happen."**

## Workflow
1.  **Pick a Task**: Run `python3 scripts/tasks.py context` to see active tasks, or `list` to see pending ones.
2.  **Plan & Document**:
    *   If starting a new task, use `scripts/tasks.py create` (or `python3 scripts/tasks.py create`) to generate a new task file.
    *   Update the task status: `python3 scripts/tasks.py update [TASK_ID] in_progress`.
3.  **Implement**: Write code, run tests.
4.  **Update Documentation Loop**:
    *   As you complete sub-tasks, check them off in the task document.
    *   If you hit a blocker, update status to `wip_blocked` and describe the issue in the file.
    *   Record key architectural decisions in the task document.
5.  **Finalize**:
    *   Update status to `completed`: `python3 scripts/tasks.py update [TASK_ID] completed`.
    *   Record actual effort in the file.
    *   Ensure all acceptance criteria are met.

## Tools
*   `python3 scripts/tasks.py create [category] "Title"`: Create a new task.
*   `python3 scripts/tasks.py list`: List all tasks.
*   `python3 scripts/tasks.py context`: List in-progress tasks.
*   `python3 scripts/tasks.py update [ID] [status]`: Update task status.

## Documentation Reference
*   **Guide**: Read `docs/tasks/GUIDE.md` for strict formatting and process rules.
*   **Architecture**: Refer to `docs/architecture/` for system design.
*   **Features**: Refer to `docs/features/` for feature specifications.

## Code Style & Standards
*   Follow the existing patterns in the codebase.
*   Ensure all new code is covered by tests (if testing infrastructure exists).
