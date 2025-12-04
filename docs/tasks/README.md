# Task Documentation System

This project uses a structured task documentation system to track work, decisions, and progress.

## Overview

All implementation tasks are documented in this directory (`docs/tasks/`). This provides a permanent record of:
- What was done
- Why it was done
- How it was done (including architectural decisions)
- What problems were encountered

## Structure

Tasks are organized by category:

- `foundation/`: Core architecture and setup
- `infrastructure/`: Services, adapters, platform code
- `domain/`: Use cases, repositories, business logic
- `presentation/`: UI, state management
- `migration/`: Refactoring and cleanup
- `features/`: End-to-end feature implementation
- `testing/`: Test infrastructure

## Workflow

1.  **Create a Task**: Use `scripts/tasks.py create` to generate a new task file.
2.  **Update Progress**: Keep the task file updated as you work.
3.  **Complete**: Mark as completed when done.

See [GUIDE.md](GUIDE.md) for detailed instructions on the format and process.
