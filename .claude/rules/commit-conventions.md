# Commit Conventions

## Format

Use conventional commits:

```
<type>: <description>

[optional body]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Types

| Type | Use For |
|------|---------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Adding/updating tests |
| `chore` | Maintenance, deps, configs |
| `style` | Formatting (no code change) |

## Rules

- Keep subject line under 72 characters
- Use imperative mood ("add" not "added")
- No period at end of subject
- Include Co-Authored-By when Claude assists
- Never force push to main/master
- Never use `git commit --amend` unless explicitly requested
