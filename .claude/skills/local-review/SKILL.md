---
name: local-review
description: Perform pre-PR automated review against the spec.
---

# Local Review Skill

Use this skill to perform an automated code review against a task's specifications to ensure implementation correctness and flag any critical issues.

## Commands

### Check Task
Compare implemented code against original task document/design spec to flag severity issues.
**Run this before transitioning a task to `review_requested`.** (Note: `scripts/tasks.py update` does this automatically).
Command: `python3 scripts/review.py check --task-id <ID>`

Example: `python3 scripts/review.py check --task-id FEATURES-20260305-171432-HBF`
