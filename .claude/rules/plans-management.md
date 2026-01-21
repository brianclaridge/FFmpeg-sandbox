# Plan Management

## When to Create Plans

Create a plan file in `.claude/plans/` when:
- Implementing multi-file features
- Making architectural changes
- User explicitly requests plan mode

Do NOT create plans for:
- Single-file bug fixes
- Simple refactors
- Research/exploration tasks

## Plan File Location

```
.claude/plans/
├── {active-plan}.md      # Current work
└── done/                 # Archived plans
    └── {timestamp}-{slug}.md
```

## Plan Template

```markdown
# Plan: {Title}

## Goal

{1-3 sentences describing the objective}

---

## Files to Modify

| File | Action | Purpose |
|------|--------|---------|
| `path/to/file` | Create/Update | Description |

---

## Implementation

### 1. {First Step}

{Details with code snippets if needed}

### 2. {Second Step}

{Details}

---

## Verification

```bash
# Commands to verify implementation
```

---

## Status: PENDING
```

## Plan Workflow

1. **Create** - Write plan file, set status to `PENDING`
2. **Execute** - Update status to `IN_PROGRESS`, work through steps
3. **Verify** - Run verification commands
4. **Archive** - Move to `done/` with execution notes

## Archiving Completed Plans

After successful implementation:

```bash
# Generate filename
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
SLUG="kebab-case-summary"

# Move to done/
mkdir -p .claude/plans/done
mv .claude/plans/{plan}.md ".claude/plans/done/${TIMESTAMP}-${SLUG}.md"
```

Append execution notes to archived plan:

```markdown
---

## Execution Notes

**Completed:** YYYY-MM-DD HH:MM
**Commit:** {hash}

**Deviations:** {any changes from original plan}
**Issues:** {problems encountered}
```

## Status Values

| Status | Meaning |
|--------|---------|
| `PENDING` | Plan created, not started |
| `IN_PROGRESS` | Currently implementing |
| `IMPLEMENTED` | Completed and archived |

## Integration with TodoWrite

Plan steps become TodoWrite items during execution. Mark todos complete as each plan step finishes.
