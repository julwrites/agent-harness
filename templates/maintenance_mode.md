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
5.  **Review & Verify**:
    *   Once implementation is complete, update status to `review_requested`: `python3 scripts/tasks.py update [TASK_ID] review_requested`.
    *   Ask a human or another agent to review the code.
    *   Once approved and tested, update status to `verified`.
6.  **Finalize**:
    *   Update status to `completed`: `python3 scripts/tasks.py update [TASK_ID] completed`.
    *   Record actual effort in the file.
    *   Ensure all acceptance criteria are met.

## Tools
*   **Wrapper**: `./scripts/tasks` (Checks for Python, recommended).
*   **Create**: `./scripts/tasks create [category] "Title"`
*   **List**: `./scripts/tasks list [--status pending]`
*   **Context**: `./scripts/tasks context`
*   **Update**: `./scripts/tasks update [ID] [status]`
*   **Migrate**: `./scripts/tasks migrate` (Migrate legacy tasks to new format)
*   **JSON Output**: Add `--format json` to any command for machine parsing.

## Documentation Reference
*   **Guide**: Read `docs/tasks/GUIDE.md` for strict formatting and process rules.
*   **Architecture**: Refer to `docs/architecture/` for system design.
*   **Features**: Refer to `docs/features/` for feature specifications.

## Code Style & Standards
*   Follow the existing patterns in the codebase.
*   Ensure all new code is covered by tests (if testing infrastructure exists).

## Agent Interoperability
- **Claude Skill**: `.claude/skills/task_manager/`
- **Tool Definitions**: `docs/interop/tool_definitions.json`
