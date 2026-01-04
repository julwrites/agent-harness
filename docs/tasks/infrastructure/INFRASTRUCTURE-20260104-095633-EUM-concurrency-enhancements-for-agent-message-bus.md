---
id: INFRASTRUCTURE-20260104-095633-EUM
status: completed
title: Concurrency Enhancements for Agent Message Bus
priority: high
created: 2026-01-04 09:56:33
category: infrastructure
dependencies: []
type: task
---

# Concurrency Enhancements for Agent Message Bus

## Context
The current message bus uses atomic writes for individual files but lacks coordination for operations involving multiple files (registry updates, archive operations). Race conditions can occur when multiple agents simultaneously read/write to the same mailboxes or registry.

## Implementation Details
1. **Advisory File Locking**: Implement `fcntl` or `portalocker` based locking for registry operations to prevent duplicate agent registrations
2. **Atomic Archive Operations**: Ensure archive moves are atomic (write to temp then rename) to prevent message loss during concurrent reads
3. **Registry Concurrency**: Add optimistic concurrency control for agent heartbeat updates
4. **Public Message Deduplication**: Prevent multiple agents from processing the same public message simultaneously
5. **Directory Locking**: Optional directory-level locking for mailbox operations

## Acceptance Criteria
- [ ] Advisory locking implemented for registry read/write operations
- [ ] Archive operations are atomic and safe for concurrent access
- [ ] No race conditions in public message processing
- [ ] Registry updates use optimistic concurrency or locking
- [ ] Backward compatibility maintained (existing agents continue to work)
- [ ] Tests demonstrate concurrent access safety with multiple simulated agents
