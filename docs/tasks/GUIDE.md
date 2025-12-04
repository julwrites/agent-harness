# Task Documentation System Guide

This guide explains how to create, maintain, and update task documentation for software development projects. It provides a reusable system for tracking implementation work, decisions, and progress that can be applied to any codebase.

## Why Document Tasks This Way?

1. **Traceability**: Every decision and implementation detail is recorded
2. **Knowledge Transfer**: New team members can understand past decisions
3. **AI Agent Context**: Provides rich context for AI assistants and automation
4. **Historical Record**: Captures the evolution of the codebase
5. **Problem Resolution**: Documents blockers and how they were resolved
6. **Effort Tracking**: Actual vs estimated effort helps future planning

## Directory Structure

Create a `docs/tasks/` directory with category-based organization:

```
docs/tasks/
├── README.md              # Overview of task system
├── foundation/            # Foundational architecture tasks
├── infrastructure/        # Infrastructure layer tasks
├── domain/               # Domain layer tasks
├── presentation/         # Presentation layer tasks
├── testing/              # Testing infrastructure
├── features/             # Feature-specific tasks
└── migration/            # Migration and refactoring tasks
```

Adjust categories based on your project's architecture (e.g., backend/frontend, services/clients, etc.).

## Task Document Template

### Required Sections

Every task document MUST include these sections:

#### 1. Task Information
```markdown
## Task Information
- **Task ID**: [CATEGORY-NNN] (e.g., FOUNDATION-001, INFRASTRUCTURE-001)
- **Status**: [pending|in_progress|completed|blocked|cancelled]
- **Priority**: [critical|high|medium|low]
- **Phase**: [1-5]
- **Estimated Effort**: [X days]
- **Actual Effort**: [X days] (update when completed)
- **Completed**: [YYYY-MM-DD] (when applicable)
- **Dependencies**: [List of task IDs or "None"]
```

**Task ID Format**:
- `FOUNDATION-NNN`: Core architecture and setup
- `INFRASTRUCTURE-NNN`: Infrastructure layer implementations
- `DOMAIN-NNN`: Domain layer implementations
- `PRESENTATION-NNN`: UI and state management
- `MIGRATION-NNN`: Refactoring and migration tasks
- `FEATURE-NNN`: Feature-specific implementations

**Status Values**:
- `pending`: Not yet started
- `in_progress`: Currently being worked on
- `wip_blocked`: Started but blocked by external issue
- `completed`: Finished and verified
- `blocked`: Cannot start due to dependencies
- `cancelled`: No longer needed
- `deferred`: Postponed to later phase

#### 2. Task Details
```markdown
## Task Details

### Description
[Clear, comprehensive description of what needs to be done and why]

### Problem Statement (if applicable)
[What problem does this solve? Why is this needed?]

### Architecture Components
- **[Layer Name]**: [How this layer is affected]
- **[Component Name]**: [Specific components involved]

### Feature Enablement
- **[Feature Name]**: [How this task enables the feature]

### Dependencies
- **[TASK-ID]**: [Dependency description and current status]

### Acceptance Criteria
- [ ] [Specific, measurable criterion 1]
- [ ] [Specific, measurable criterion 2]
- [x] [Completed criterion]

### Implementation Notes
- [Technical considerations]
- [Approach decisions]
- [Trade-offs made]
```

#### 3. Implementation Status

```markdown
## Implementation Status

### Architecture Decision (if applicable)
[Explain architectural patterns and why they were chosen]

### Completed Work
- ✅ [Specific accomplishment with file references]
- ✅ [Another accomplishment]
- ⚠️ [Partial completion or caveat]

### Current Blockers (when status is blocked/wip_blocked)
**[Blocker Title]**:
```
[Error messages or issue description]
```

**Resolution Strategy**:
1. [Step to resolve]
2. [Next step]

### Remaining Work
- [What still needs to be done]
- [Future enhancements]
- [Items deferred to later phases]

### Git History
- Commit [hash]: [Description of what was committed]
- Commit [hash]: [Next commit description]
```

#### 4. Optional Sections

Include these when relevant:

**Code Examples**:
```markdown
### Implementation Example
\`\`\`language
// Show correct implementation patterns
// Include comments explaining key decisions
\`\`\`
```

**API Usage**:
```markdown
### Correct API Pattern
**Package**: package_name

\`\`\`language
// Demonstrate correct usage
\`\`\`

**Common Mistakes**:
- [What to avoid]
- [Why it's wrong]
```

**Related Tasks**:
```markdown
### Related Tasks
- **[TASK-ID]**: [How they relate]
```

#### 5. Metadata Footer

Every document ends with:
```markdown
---

*Created: YYYY-MM-DD*
*Last updated: YYYY-MM-DD*
*Status: [current status] - [Brief status note]*
```

## Creating a New Task Document

### Step 1: Choose the Right Category

Place the task in the appropriate directory:
- **foundation/**: Core architecture, DI, project structure
- **infrastructure/**: Services, adapters, platform code
- **domain/**: Use cases, repositories, business logic
- **presentation/**: UI, state management, navigation
- **migration/**: Refactoring, package migrations
- **features/**: End-to-end feature implementation

### Step 2: Generate and Create Task

Use the provided script to generate the task file with a unique ID:

```bash
# Usage: python3 scripts/tasks.py create [category] "Title" --desc "Description"
python3 scripts/tasks.py create foundation "Initial Setup"
```

This will automatically:
1. Find the next available ID (e.g., FOUNDATION-001).
2. Create the file `docs/tasks/foundation/FOUNDATION-001-initial-setup.md`.
3. Populate it with the standard template.

## Updating Task Documents

### When Starting a Task

1. Change status to `in_progress`
2. Add **Implementation Status** section
3. Note start date in metadata

```markdown
## Task Information
- **Status**: in_progress
- **Started**: 2025-MM-DD
```

### During Implementation

Update the document as you work:

1. **Mark acceptance criteria** as you complete them:
```markdown
- [x] ~~Criterion completed~~ ✅
- [ ] Criterion in progress
```

2. **Document completed work** with file references:
```markdown
### Completed Work
- ✅ Created NfcService interface (lib/core/infrastructure/services/nfc_service.dart)
- ✅ Implemented checkAvailability() method (lines 14-23)
```

3. **Record git commits**:
```markdown
### Git History
- Commit abc1234: Add NFC service interface
- Commit def5678: Implement availability check
```

4. **Document blockers immediately**:
```markdown
### Current Blockers
**Package API Mismatch**:
```
error • Undefined class 'NdefMessage'
```

**Resolution Strategy**:
1. Check package documentation at [URL]
2. Examine working implementation in main.dart
3. Update imports and API calls
```

### When Blocked

1. Change status to `wip_blocked` or `blocked`
2. Add **Current Blockers** section with:
   - Clear description of the blocker
   - Error messages or reproduction steps
   - Resolution strategy
3. Update metadata:

```markdown
## Task Information
- **Status**: wip_blocked
- **Actual Effort**: X days (blocked on [issue])

### Current Blockers
[Detailed blocker information]
```

### When Unblocking

1. Document how the blocker was resolved:
```markdown
### Completed Work
- ✅ Resolved package API issue by examining main.dart implementation
- ✅ Updated imports to use correct package paths
```

2. Remove **Current Blockers** section or move to history
3. Update status to `in_progress` or `completed`

### When Completing a Task

1. **Mark all acceptance criteria** as complete:
```markdown
### Acceptance Criteria
- [x] All criteria met
```

2. **Update status and effort**:
```markdown
## Task Information
- **Status**: completed
- **Actual Effort**: X days
- **Completed**: 2025-MM-DD
```

3. **Finalize completed work section**:
```markdown
### Completed Work
- ✅ [Everything accomplished]

### Git History
- Commit abc1234: [First commit]
- Commit def5678: [Final commit]
```

4. **Move remaining work** to future tasks or note deferral:
```markdown
### Remaining Work
- Advanced feature X (deferred to Phase 2)
- Performance optimization Y (deferred to Phase 3)
```

5. **Update metadata**:
```markdown
---

*Created: 2025-MM-DD*
*Completed: 2025-MM-DD*
*Status: completed - [Brief achievement summary]*
```

## Best Practices

### 1. Be Specific with File References

**Good**:
```markdown
- ✅ Created NfcService interface (lib/core/infrastructure/services/nfc_service.dart:10-25)
```

**Bad**:
```markdown
- ✅ Created some files
```

### 2. Document Decisions and Trade-offs

```markdown
### Architecture Decision
Chose sealed classes over enums for error types because:
1. Allows carrying additional context per error type
2. Enables exhaustive pattern matching
3. Better type safety for error handling

Trade-off: Slightly more verbose than simple enums
```

### 3. Include Code Examples for Complex Tasks

```markdown
### Implementation Example

**Correct NDEF Record Creation**:
\`\`\`dart
final payload = Uint8List.fromList([
  languageCode.length,
  ...languageCode.codeUnits,
  ...text.codeUnits,
]);

final textRecord = NdefRecord(
  typeNameFormat: TypeNameFormat.wellKnown,
  type: Uint8List.fromList('T'.codeUnits),
  payload: payload,
);
\`\`\`
```

### 4. Link Related Tasks

```markdown
### Related Tasks
- **FOUNDATION-003**: Provides domain models used here
- **INFRASTRUCTURE-002**: Depends on this service implementation
- **DOMAIN-001**: Consumes this service
```

### 5. Track Actual vs Estimated Effort

This helps improve future estimates:

```markdown
## Task Information
- **Estimated Effort**: 3 days
- **Actual Effort**: 1.5 days

### Notes on Effort
Task completed faster because:
- Existing implementation in main.dart provided clear pattern
- Package API documentation was accurate
```

### 6. Document Errors with Context

**Good**:
```markdown
### Current Blockers
**NdefMessage Type Conflict**:
```
error • Undefined class 'NdefMessage' • lib/.../nfc_service_impl.dart:91:25
```

**Cause**: Incorrect import - NdefMessage is in nfc_manager/ndef_record.dart, not nfc_manager_ndef

**Resolution**: Add correct import statement
```

**Bad**:
```markdown
### Blockers
- Some error with NdefMessage
```

### 7. Keep Implementation Status Current

Update the **Completed Work** section after each commit:

```markdown
### Completed Work
- ✅ Created service interface (commit abc1234)
- ✅ Implemented availability check (commit def5678)
- ✅ Added error handling (commit ghi9012)

### Git History
- Commit abc1234: Add NFC service interface
- Commit def5678: Implement availability check
- Commit ghi9012: Add comprehensive error handling
```

## Common Scenarios

### Scenario 1: Package API Migration

**Initial State** (when blocked):
```markdown
## Task Information
- **Status**: wip_blocked
- **Actual Effort**: 1 day (blocked on package API verification)

### Current Blockers
**Package API Inconsistencies**:
[Error messages]

**Resolution Strategy**:
1. Examine working implementation
2. Verify correct API usage
3. Update implementation
```

**After Resolution**:
```markdown
## Task Information
- **Status**: completed
- **Actual Effort**: 1.5 days (0.5 days to resolve blocker)

### Completed Work
- ✅ Resolved package API issues via MIGRATION-001
- ✅ Updated all imports to correct packages
- ✅ Verified with flutter analyze (zero errors)

### Git History
- Commit abc1234: WIP implementation with blockers
- Commit def5678: Fixed package API usage
- Commit ghi9012: Updated documentation
```

### Scenario 2: Adding New Features

```markdown
# Task: User Authentication

## Task Information
- **Task ID**: FEATURE-001
- **Status**: in_progress
- **Phase**: 2
- **Estimated Effort**: 3 days
- **Dependencies**: INFRASTRUCTURE-001 (completed)

### Acceptance Criteria
- [x] User registration flow
- [x] Login/logout functionality
- [ ] Password reset
- [ ] Session management

### Completed Work
- ✅ Implemented registration UI (lib/features/auth/pages/register_page.dart)
- ✅ Created AuthBloc for state management (lib/features/auth/bloc/auth_bloc.dart)
- ⚠️ Password reset partially complete - email integration pending
```

### Scenario 3: Refactoring Tasks

```markdown
# Task: Migrate to Riverpod State Management

## Task Information
- **Task ID**: MIGRATION-002
- **Status**: pending
- **Priority**: medium
- **Phase**: 2
- **Dependencies**: PRESENTATION-001 (BLoC implementation completed)

### Description
Migrate from BLoC to Riverpod for improved developer experience and reduced boilerplate.

### Migration Strategy
1. Install Riverpod packages
2. Create providers for existing BLoCs
3. Update widgets to use ConsumerWidget
4. Remove BLoC dependencies
5. Update tests

### Acceptance Criteria
- [ ] All BLoCs converted to Riverpod providers
- [ ] All screens use ConsumerWidget
- [ ] All tests passing
- [ ] No BLoC dependencies remaining
```

## Checklist for Task Documentation

Use this checklist when creating or updating task documents:

### New Task Document
- [ ] Unique Task ID assigned
- [ ] Placed in correct category directory
- [ ] All required sections present
- [ ] Dependencies clearly listed
- [ ] Acceptance criteria specific and measurable
- [ ] Metadata footer included

### In-Progress Updates
- [ ] Status updated to in_progress
- [ ] Completed work section added
- [ ] Git commits documented
- [ ] Blockers documented (if any)
- [ ] Acceptance criteria progress tracked

### Completion Updates
- [ ] All acceptance criteria checked
- [ ] Status updated to completed
- [ ] Actual effort recorded
- [ ] Completion date added
- [ ] Git history complete
- [ ] Remaining work documented
- [ ] Metadata footer updated

### Blocker Documentation
- [ ] Status updated to wip_blocked or blocked
- [ ] Clear blocker description
- [ ] Error messages included
- [ ] Resolution strategy documented
- [ ] Related tasks notified

## Tools and Automation

### Managing Tasks

Use the `scripts/tasks.py` script to manage tasks.

```bash
# Create a new task
python3 scripts/tasks.py create [category] "Task Title"

# List tasks
python3 scripts/tasks.py list

# List pending tasks
python3 scripts/tasks.py list --status pending
```

### Validating Task Documents

```bash
# Check for required sections
for file in docs/tasks/**/*.md; do
  if ! grep -q "## Task Information" "$file"; then
    echo "Missing Task Information: $file"
  fi
done
```

### Generating Task Summary

```bash
# Count tasks by status
echo "Task Status Summary:"
grep -rh "Status**:" docs/tasks/ | sort | uniq -c
```

## Integration with AI Agents

This documentation system is designed to work seamlessly with AI coding assistants. To integrate with your AI agent configuration (e.g., AGENTS.md, .cursorrules, etc.):

### Example AI Agent Instructions

```markdown
## Task Documentation System

All implementation tasks are documented in `docs/tasks/` following a standardized format. When working on tasks:

1. **Before starting**: Read the task document in docs/tasks/[category]/
2. **During work**: Update the task document with progress, blockers, and decisions
3. **After completion**: Mark acceptance criteria complete and update status
4. **When blocked**: Document the blocker with error messages and resolution strategy

### Task Document Locations
- Foundation: docs/tasks/foundation/
- Infrastructure: docs/tasks/infrastructure/
- Domain: docs/tasks/domain/
- Migrations: docs/tasks/migration/

### Key Documentation Principles
- Include file references with line numbers
- Document all architectural decisions
- Record actual vs estimated effort
- Link related tasks
- Preserve error messages and resolution strategies
```

## Maintaining Documentation Quality

### Weekly Review

1. **Check for stale tasks**: Tasks in `in_progress` for > 1 week
2. **Update blocked tasks**: Verify blockers are still valid
3. **Cross-reference dependencies**: Ensure dependency status is current
4. **Verify git history**: Ensure all commits are documented

### Monthly Audit

1. **Effort accuracy**: Compare estimated vs actual effort
2. **Completion rate**: Track percentage of completed tasks
3. **Blocker patterns**: Identify recurring blockers
4. **Documentation gaps**: Find tasks missing key sections

## Getting Started

To bootstrap this system in your repository:

1. **Create directory structure**:
```bash
mkdir -p docs/tasks/{foundation,infrastructure,domain,presentation,migration,features,testing}
```

2. **Copy this guide**:
```bash
cp task-documentation-guide.md docs/tasks/GUIDE.md
```

3. **Create tasks README**:
```bash
# Create docs/tasks/README.md with project-specific overview
```

4. **Create first task**:
```bash
# Use the template to create your first task document
```

5. **Update AI agent config**:
```bash
# Add task documentation instructions to AGENTS.md or similar
```

## Conclusion

Good task documentation is an investment that pays dividends through:
- Faster onboarding of new team members
- Better context for AI assistants
- Historical record of decisions
- Improved future estimates
- Easier debugging and problem resolution

When in doubt, document more rather than less. Future you (and your team) will thank you.

---

*This is a reusable template - adapt categories and sections to your project's needs*
*Created: 2025-02-11*
