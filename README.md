# AI-Assisted Project Bootstrapper

This repository provides a standardized foundation for AI-assisted coding projects. It includes a robust Task Documentation System, Memory Management, and AI Agent Instructions to streamline collaboration between human developers and AI agents.

## Features

*   **Task Management**: Structured task tracking using Markdown and YAML Frontmatter.
*   **Memory System**: Long-term knowledge storage for the project.
*   **Agent Instructions**: Pre-configured `AGENTS.md` (and `CLAUDE.md`) to guide AI behavior.
*   **Automation**: Python scripts for task creation, status updates, and dependency management.
*   **Agile Support**: Built-in support for Sprints, Estimations, and Epics/Stories.

## Getting Started

### 1. Bootstrap the Project

If you have just cloned this repository to start a new project:

1.  **Initialize Directory Structure**:
    ```bash
    python3 scripts/tasks.py init
    ```
    This will create the `docs/` hierarchy and ensure all necessary configuration files are in place.

2.  **Create Your First Task**:
    ```bash
    python3 scripts/tasks.py create foundation "Initial Project Setup"
    ```

3.  **Install Pre-Commit Hooks** (Optional but Recommended):
    ```bash
    python3 scripts/tasks.py install-hooks
    ```
    This ensures task validity before every commit.

### 2. Workflow

The core workflow is centered around `scripts/tasks.py` (or the `./scripts/tasks` wrapper).

*   **List Tasks**: `./scripts/tasks list`
*   **Create Task**: `./scripts/tasks create features "New Feature"`
*   **Start Work**: `./scripts/tasks update [TASK_ID] in_progress`
*   **Complete Work**: `./scripts/tasks update [TASK_ID] verified` -> `completed`

For detailed instructions, refer to [docs/tasks/GUIDE.md](docs/tasks/GUIDE.md).

## For AI Agents

Refer to [AGENTS.md](AGENTS.md) for detailed operational instructions. This file serves as the "System Prompt" extension for agents working in this repository.

## Directory Structure

*   `docs/tasks/`: Active and completed tasks.
*   `docs/memories/`: Long-term project context.
*   `docs/architecture/`: System design documentation.
*   `scripts/`: Automation tools (`tasks.py`, `memory.py`, `bootstrap.py`).
*   `templates/`: Templates for tasks and guides.

## Maintenance

To upgrade the bootstrapper scripts or switch to maintenance mode, use `scripts/bootstrap.py`.

```bash
python3 scripts/bootstrap.py finalize
```
