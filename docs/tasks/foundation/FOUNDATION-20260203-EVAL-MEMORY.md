---
id: FOUNDATION-20260203-EVAL-MEMORY
status: pending
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

1. [ ] **Prototype Multi-Lens Compaction**:
    - Update `scripts/tasks.py compact` to ask LLM for structured sections: `## Technical`, `## Decisions`, `## Unresolved`.
2. [ ] **Entity Indexer**:
    - Create `scripts/memory.py index` to scan `docs/tasks/` and build a `docs/memories/entities.json` map (Entity -> [Task IDs]).
3. [ ] **Hyperlink Enforcer**:
    - Ensure all references to other tasks/files in summaries are explicit absolute paths or relative links to allow `cat` to follow them.

## Acceptance Criteria
- [ ] Feasibility prototype of "Entity Indexer" (is it too expensive to run on every task?).
- [ ] Decision on "Multi-Lens" schema for Archived Tasks.
