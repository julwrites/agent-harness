# Bootstrapper Critique & Improvement Plan

## Executive Summary
The bootstrapping system is a solid, dependency-free foundation for maintaining context within a repository. The "Task Documentation System" philosophy is excellent for AI-assisted development. However, the implementation relies on fragile string parsing for metadata management and has some usability gaps that could friction for developers.

## Detailed Critique

### 1. Robustness & Code Quality
*   **Fragile Metadata Updates**: The `update_task_status` function in `scripts/tasks.py` relies on `line.startswith("status:")`. This fails if a user manually edits the file and adds indentation (e.g., ` status: pending`) or comments.
*   **ID Collision Risk**: `generate_task_id` uses one-second resolution (`%Y%m%d-%H%M%S`). Scripted bulk creation of tasks will cause ID collisions.
*   **Repo State Detection**: `scripts/bootstrap.py` checks for specific directories (`src`, `lib`) to determine if a repo is "new" or "existing". This is language-specific and may misidentify existing Go, Rust, or flat-structure projects.

### 2. Usability (Developer Experience)
*   **Task Management Friction**: marking a task as done requires typing `update [ID] completed`. A simple `complete [ID]` alias would save time.
*   **Search/Find**: `find_task_file` iterates strictly. As the project grows, finding tasks might become slightly slower, though likely negligible for documentation.
*   **Input Validation**: The `create` command does not support setting `priority` or initial `status`, defaulting everything to `medium`/`pending`.

### 3. Documentation & Workflow
*   **Bootstrap Finalization**: The `finalize` step blindly overwrites `AGENTS.md` with the maintenance template. While it creates a backup, a merge or diff approach might be safer if the user has added custom instructions during bootstrapping.

## Suggestions for Improvement

### Immediate Fixes (Code Quality)
1.  **Robust Frontmatter Parsing**: Update `tasks.py` to use a more flexible regex-based substitution for updating fields, allowing for whitespace variations.
2.  **Safe ID Generation**: Append a short random suffix or use a monotonic counter if multiple tasks are created in the same second.

### Feature Enhancements
1.  **CLI Shortcuts**: Add `complete` and `verify` commands to `tasks.py` as shortcuts for status updates.
2.  **Smart Init**: Update `bootstrap.py` to detect `.git` history or file count as a better heuristic for "Existing Repository".
3.  **Enhanced Create**: Allow `scripts/tasks.py create --priority high --status in_progress ...`.

### Long-term
1.  **Validation Hook**: Add a git pre-commit hook (optional install) to ensure task files are valid YAML/Markdown before committing.
