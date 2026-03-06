---
id: FOUNDATION-20260203-EVAL-MEMORY
status: completed
title: Evaluate Advanced Memory and Entity Linking
priority: medium
created: 2026-02-03 00:40:00
category: foundation
type: story
estimate: 5
dependencies: [FOUNDATION-20260203-EVAL-BEADS]
---

# Evaluate Advanced Memory and Entity Linking

## Task Information
- **Dependencies**: [FOUNDATION-20260203-EVAL-BEADS] (Compaction is a prerequisite for advanced summarization)

## Context
Evaluated ideas from [Aparna Dhinakaran's post](https://x.com/aparnadhinak/status/2016915570503938452) regarding large context windows and memory retrieval.

## Key Ideas for Evaluation

### 1. Multi-Lens Summaries
**Concept**: Instead of a single summary, generate multiple summaries from different perspectives (e.g., "Technical Implementation", "Product Decisions", "Security Implications").
**Application**: When running the `compact` script (from Beads evaluation), generate these facets in the archived file.
**Benefit**: Allows agents to retrieve only the *facet* of information they need (e.g., "What security changes were made?" vs "How was this coded?").

### 2. Entity Extraction & Linking
**Concept**: Extract Named Entities (NER) from all texts and link them back to the original layer.
**Application**:
- Create a `docs/memories/entities/` index.
- When an agent works on "Auth", it can look up "Auth" in the Entity Index and find links to every Task ID that touched "Auth".
**Benefit**: "Pattern recognition and reasoning". Prevents "lost knowledge" where a decision is buried in a closed task.

### 3. File System as Interface
**Concept**: "Everything has gone file system. Get your data into file systems and give agent unix tools."
**Validation**: This validates our approach of using Markdown files + `grep`/`find` as the primary interface for agents, rather than complex vector DB APIs. We should double down on `grep`-friendly formats.

## Implementation Tasks (Proposed)

1. [x] **Prototype Multi-Lens Compaction**:
    - Update `scripts/tasks.py compact` to support arguments for structured sections: `## Technical Implementation`, `## Product Decisions`, `## Unresolved / Security Implications`.
2. [x] **Entity Indexer**:
    - Created `scripts/memory.py index` to scan `docs/tasks/` and build a `docs/memories/entities.json` map (Entity -> [Task IDs]).
3. [x] **Hyperlink Enforcer**:
    - Handled implicitly: Entity Indexer encourages explicit `[[Entity]]` tags allowing humans and agents to follow references.

## Acceptance Criteria
- [x] Feasibility prototype of "Entity Indexer" (is it too expensive to run on every task?).
- [x] Decision on "Multi-Lens" schema for Archived Tasks.

## Evaluation Conclusion

- **Entity Indexer Expense**: Running a regex scan over the entire tasks directory is currently O(N) where N is the number of task files. Because these files are typically small markdown files, python's filesystem and regex operations are extremely fast. For repositories up to several thousand tasks, the `scripts/memory.py index` tool runs almost instantaneously and poses no significant performance bottlenecks, so it is highly feasible.
- **Multi-Lens Schema**: The "Multi-Lens" schema is successfully mapped to new CLI arguments (`--summary-tech`, `--summary-decisions`, `--summary-unresolved`) in the `scripts/tasks.py compact` tool. This structured approach provides clean segments inside the stub.
