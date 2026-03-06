---
id: FEATURES-20260305-171341-JOO
status: pending
title: Implement Phase 2 Granular Execution TDD Enforcer
priority: medium
created: 2026-03-05 17:13:41
dependencies:
type: task
part_of: [FEATURES-20260305-085909-JDI]
---

# Implement Phase 2 Granular Execution TDD Enforcer

Implement the `tdd-enforcer` Skill (.claude/skills/tdd/) and its backing script `scripts/tdd.py`.

The purpose of this skill is to enforce the RED-GREEN-REFACTOR cycle.

Functionality:
- Acts as a state-machine tool that the agent must call.
- State 1: Run test (must fail).
- State 2: Implement code.
- State 3: Run test (must pass).
- State 4: Refactor.
- Deletes code written before tests to enforce TDD.
