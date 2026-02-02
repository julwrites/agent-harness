# Migration Guide: Agent Harness V2 (Graph & Memory)

This guide provides instructions for Agents and Developers migrating from the legacy List-based Task system to the new **Graph-based** and **Memory-enhanced** system (V2).

## 1. Task Frontmatter Updates

The primary change is moving from a simple `dependencies` list to typed relationships.

### Before (Legacy)
```yaml
dependencies: [TASK-001, TASK-002]
```

### After (V2)
You must classify the relationship.

```yaml
relationships:
  depends_on: [TASK-001]      # Blocking dependency (cannot start until TASK-001 is verified)
  part_of:    [EPIC-100]      # Parent task/Epic
  related_to: [TASK-005]      # Contextual link, not blocking
```

**Action Required**:
- run `./scripts/tasks.py migrate --v2` (Once implemented) to auto-convert existing `dependencies` to `depends_on`.
- Manually review identifying `part_of` relationships for better grouping.

## 2. Workflow Changes

### Finding Work (`auto-ready`)
**Legacy**: You had to look at `pending` tasks and check dependencies manually or trust a basic sort.
**V2**: Use the `ready` command.
```bash
./scripts/tasks.py ready
```
*This command ONLY returns tasks where ALL `depends_on` ancestors are `verified`.*

### completing Tasks (Compaction)
**Legacy**: You marked a task `completed` and left the full file.
**V2**: When a task is fully done, you *must* compact it to save context for future agents.
```bash
./scripts/tasks.py compact [TASK_ID]
```
*This will trigger an LLM flow to summarize the task into `docs/archive/` and delete the detailed markdown file.*

## 3. Using Memory & Entity Links
New to V2 is the **Entity Index**.

- **Before**: You searched `grep "Auth" docs/tasks`.
- **After**: Check the Entity Index first.
```bash
cat docs/memories/entities.json | grep "Auth"
```
This returns a list of Task IDs that are semantically linked to "Auth", even if they don't contain the exact keyword in the title.

## 4. Prompts & Personas
If you need to switch context (e.g., from "Architect" to "Tester"), check `prompts/personas/`.
```bash
cat prompts/personas/tester.md
```

## Migration Checklist for Agents
1. [ ] **Update your internal prompt/instructions**: Stop looking for `dependencies: []`. Look for `relationships: {}`.
2. [ ] **Adopt `ready` command**: Stop guessing what to work on.
3. [ ] **Compact your work**: Don't leave messy files behind.
