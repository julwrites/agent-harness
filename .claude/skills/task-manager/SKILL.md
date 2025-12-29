---
name: task-manager
description: Manage development tasks using the repository's task system. Allows creating, listing, updating, and viewing tasks.
---

# Task Manager Skill

This skill allows you to manage development tasks tracked in the `docs/tasks/` directory.
It uses the `scripts/tasks` utility.

## Commands

### List Tasks
List all tasks or filter by status/category.
Command: `./scripts/tasks list [--status <status>] [--category <category>] [--format json]`

### Create Task
Create a new task.
Command: `./scripts/tasks create <category> "<title>" [--desc "<description>"] [--format json]`
Categories: foundation, infrastructure, domain, presentation, migration, features, testing, review, security, research

### Show Task
Show details of a specific task.
Command: `./scripts/tasks show <task_id> [--format json]`

### Update Task Status
Update the status of a task.
Command: `./scripts/tasks update <task_id> <status> [--format json]`
Valid statuses: pending, in_progress, wip_blocked, review_requested, verified, completed, blocked, cancelled, deferred

### Manage Dependencies
Link or unlink tasks to manage dependencies.
- Add Dependency: `./scripts/tasks link <task_id> <dependency_id> [--format json]`
- Remove Dependency: `./scripts/tasks unlink <task_id> <dependency_id> [--format json]`

### Visualize Tasks
Visualize the task dependency graph.
Command: `./scripts/tasks graph [--format json]` (or `visualize`)

### Generate Index
Generate the task dependency index file (`docs/tasks/INDEX.yaml`).
Command: `./scripts/tasks index [--format json]`

### Get Context
Show currently in-progress tasks.
Command: `./scripts/tasks context [--format json]`

### Delete Task
Delete a task.
Command: `./scripts/tasks delete <task_id> [--format json]`

### Archive Task
Archive a completed task.
Command: `./scripts/tasks archive <task_id> [--format json]`

## Usage Instructions
- Always use `./scripts/tasks context` to see what is currently being worked on before starting new work.
- When creating a task, choose the appropriate category.
- Use `--format json` when you need to parse the output programmatically.
