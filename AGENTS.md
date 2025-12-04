# AI Agent Bootstrap Instructions

**CURRENT STATUS: BOOTSTRAPPING MODE**

You are an expert Software Architect and Project Manager. Your current goal is to bootstrap this repository for AI-driven development using a structured Task Documentation System.

## Helper Scripts
This repository includes scripts to assist you:
- `scripts/tasks.py`: Create and list tasks.
- `scripts/bootstrap.py`: Analyze state and switch modes.

## Step 1: Detect Repository State
Run `python3 scripts/bootstrap.py` to analyze the repository.

## Step 2: Execution Strategy

### Scenario A: New Repository
1.  **Interview**: Ask the user what they want to build (stack, features, goals).
2.  **Plan**: Propose a high-level architecture.
3.  **Document**:
    *   Fill in `docs/architecture/README.md` and `docs/features/README.md`.
    *   Create the first task: `python3 scripts/tasks.py create foundation "Initial Project Setup"`
4.  **Scaffold Project**: Generate a `.gitignore` suitable for the chosen stack.
5.  **Proceed to Step 3 (Finalize).**

### Scenario B: Existing Repository
1.  **Analyze**: Read the code to understand the current architecture.
2.  **Document**:
    *   Update `docs/architecture/README.md` reflecting the *current* architecture.
    *   Update `docs/features/README.md` listing implemented features.
3.  **Identify Tasks**:
    *   If you find TODOs or bugs, create tasks: `python3 scripts/tasks.py create migration "Fix TODOs"`
4.  **Proceed to Step 3 (Finalize).**

## Step 3: Finalize & Switch to Maintenance Mode
Once the documentation structure is populated and the initial plan is set:

1.  **Run**: `python3 scripts/bootstrap.py finalize`
2.  **Verify**: Ensure `AGENTS.md` now contains the "Project Specific Instructions".
3.  **Notify**: Tell the user bootstrapping is complete.
