# Bootstrapper Critique & Improvement Plan

## Executive Summary
The bootstrapping system is a solid, dependency-free foundation for maintaining context within a repository. The "Task Documentation System" philosophy is excellent for AI-assisted development. Recent updates have addressed robustness issues, performance optimizations, and safety checks.

## Resolved Issues

### 1. Robustness & Code Quality
*   **FIXED** - **Fragile Metadata Updates**: `scripts/tasks.py` now uses robust regex-based parsing for frontmatter extraction and status updates.
*   **FIXED** - **ID Collision Risk**: `generate_task_id` now appends a random suffix to the timestamp.
*   **FIXED** - **Repo State Detection**: `scripts/bootstrap.py` now checks for `.git` directory presence.
*   **FIXED** - **Validation**: Added `validate` command and `install-hooks` to ensure data integrity and prevent invalid task files.
*   **FIXED** - **Circular Dependency Detection**: `scripts/tasks.py` now performs cycle detection in task dependencies during validation.

### 2. Usability (Developer Experience)
*   **FIXED** - **Task Management Friction**: `complete` command alias added.
*   **FIXED** - **Input Validation**: `create` command supports `--priority` and `--status`.
*   **FIXED** - **Search Performance**: `find_task_file` optimized to use category directory lookup when possible, avoiding full tree traversal for standard task IDs.

### 3. Documentation & Workflow
*   **FIXED** - **Safety Warnings**: `scripts/bootstrap.py` now explicitly warns about backing up custom `AGENTS.md` content and prompts for hook installation.
*   **FIXED** - **Bootstrap Finalization**: `scripts/bootstrap.py` now automatically extracts and preserves custom preamble text (context added before the first header) in addition to custom headers. It filters out standard bootstrapping instructions while keeping user-added context.

### 4. New Features
*   **Implemented** - **Task Dependencies**: Added support for tracking dependencies between tasks via `dependencies` frontmatter field. Dependencies are validated and displayed.
*   **Implemented** - **Visualization**: Added `visualize` command to generate Mermaid diagrams of task dependencies, color-coded by status.

### 5. Maintenance & Reliability
*   **Implemented** - **Self-Testing**: Added `tests/test_tasks.py` with unit tests covering core functionality and regression tests for known bugs.
*   **FIXED** - **Search Robustness**: `find_task_file` now correctly falls back to a full search if the optimized category lookup fails (e.g., if a task was moved).
*   **FIXED** - **Nested Directory Support**: `list_tasks` now correctly filters by category even if tasks are located in subdirectories.
*   **Implemented** - **Archiving**: Added `archive` command to move completed tasks to `docs/tasks/archive/`, keeping the active view clean. `list` command excludes archived tasks by default.

## Remaining Critique

### 1. Documentation & Workflow
*   **NOTE** - **Manual Verification**: While `finalize` now preserves custom sections and preamble, manual verification against `AGENTS.md.bak` is still recommended as a safety precaution.

### 2. Configuration
*   **NOTE** - **Hardcoded Categories**: Categories are currently hardcoded in `scripts/tasks.py`. Making them configurable would improve flexibility for different project types.

## Future Suggestions

### Long-term
1.  **Interactive Merge**: Implement a more sophisticated `finalize` process that could use an LLM or 3-way merge to blend instructions intelligently.
2.  **Web Interface**: A simple local web server to view and manage tasks graphically.
