---
id: FEATURES-20260305-171432-HBF
status: completed
title: Implement Phase 3 Subagent Orchestration Local Code Review
priority: medium
created: 2026-03-05 17:14:32
dependencies:
type: task
part_of: [FEATURES-20260305-085909-JDI]
---

# Implement Phase 3 Subagent Orchestration Local Code Review

Implement the `local-review` Skill (.claude/skills/local-review/) and its backing script `scripts/review.py`.

The purpose of this skill is to perform a pre-PR automated review against the spec.

Functionality:
- Compares the implemented code against the original task document/design spec.
- Flags severity issues.
- Blocks the transition to `review_requested` if critical issues are found.
