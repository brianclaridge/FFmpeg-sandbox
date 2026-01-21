# Agent Consideration

Before responding to implementation or maintenance tasks, evaluate if specialized agents would help.

## Available Agents

| Agent | Color | Expertise |
|-------|-------|-----------|
| rust-maintainer | orange | Rust code quality, cross-platform builds |
| python-maintainer | yellow | Python scripts, PEP 723, hooks |
| hook-validator | cyan | Hook configuration, event handling |
| plugin-tester | green | E2E testing, plugin validation |
| plugin-manifest | blue | plugin.json validation |
| skill-author | purple | SKILL.md creation and quality |
| release-manager | red | Versioning, changelogs, releases |

## When to Use Agents

- **rust-maintainer**: Rust code changes, dependency updates, cross-platform issues
- **python-maintainer**: Hook scripts, Python utilities, PEP 723 compliance
- **hook-validator**: New hooks, hook debugging, event routing
- **plugin-tester**: Before releases, after structural changes
- **plugin-manifest**: New plugins, version bumps
- **skill-author**: New skills, skill documentation
- **release-manager**: Version bumps, changelog updates, releases

## Agent Coordination Patterns

### Sequential Workflows

For dependent tasks, chain agents sequentially:

1. **Plan → Implement → Review**
   - code-explorer → code-architect → code-reviewer

2. **Build → Test → Release**
   - rust-maintainer → plugin-tester → release-manager

### Parallel Verification

For independent checks, run agents in parallel:

```
├── rust-maintainer (code review)
├── hook-validator (hook config)
└── plugin-tester (integration tests)
```

## Model Selection Guidance

| Model | Use Case |
|-------|----------|
| `sonnet` | Feature development, complex analysis, code generation |
| `opus` | Architectural decisions, complex reasoning, critical reviews |
| `haiku` | Quick validation, simple checks, fast feedback |
| `inherit` | Specialty agents, maintain parent context model |

### Selection Guidelines

- **Default to `inherit`** unless specific model needed
- **Use `sonnet`** for most feature work
- **Use `opus`** for complex architectural analysis
- **Use `haiku`** for fast, simple validations

## Confidence Scoring Patterns

Agents should report confidence in their outputs:

### 0-100 Scale

```markdown
## Analysis Results
Confidence: 85/100

### Findings
- Finding 1 (high confidence)
- Finding 2 (medium confidence)
```

### 1-10 Scale

```markdown
## Review Complete
Confidence: 8/10

### Summary
The implementation follows best practices...
```

### Confidence Thresholds

| Score | Interpretation | Action |
|-------|----------------|--------|
| 90-100 | High confidence | Proceed automatically |
| 70-89 | Medium confidence | Proceed with caution |
| 50-69 | Low confidence | Request human review |
| <50 | Very low confidence | Escalate to user |

## Include in Responses

For non-trivial tasks, include a brief agent analysis:

```markdown
## Agent Analysis
| Agent | Used? | Reason |
|-------|-------|--------|
| rust-maintainer | Yes | Modifying Rust code |
| hook-validator | No | No hook changes |
| plugin-tester | Pending | Will run after changes |
```

This ensures thoughtful delegation and documents reasoning.

## Agent Description Pattern

Agent descriptions must include `<example>` tags:

```yaml
description: Use this agent when the user asks to "trigger phrase", "another phrase", or mentions "keyword". <example>Context: User situation\nuser: "User message"\nassistant: "I'll use the agent-name agent to..."\n<commentary>Why this agent triggers</commentary></example>
```

See individual agent files for examples.
