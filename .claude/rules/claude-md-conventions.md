# CLAUDE.md Conventions

## Quick Reference

| Question | Answer |
| -------- | ------ |
| Location? | Root of project or plugin folder |
| When to update? | New tools, conventions, critical patterns |
| Format? | Terse sections with tables and lists |
| Purpose? | Claude Code project-level instructions |

---

**IMPORTANT** CLAUDE.md provides project-specific instructions that override defaults. Keep it current as the project evolves.

## File Purpose

CLAUDE.md is read by Claude Code at session start. Contents:

- Project conventions (languages, frameworks, tools)
- Build commands and test procedures
- Critical patterns and anti-patterns
- Plugin-specific usage instructions

## When to Update

| Event | Action |
| ----- | ------ |
| New tool adopted | Add to conventions section |
| Build process changed | Update build commands |
| Critical bug pattern discovered | Add to anti-patterns |
| New CLI flags needed | Update usage examples |

## When NOT to Update

- Session-specific context
- Transient information that changes frequently
- Detailed implementation notes (use code comments)

## Content Guidelines

### Structure

```markdown
# plugin-name

One-line description.

## Installation

[Build and load instructions]

## Usage

[CLI examples, common patterns]

## Architecture

[Key components, data flow]
```

### Style

- **Terse** - Bullet points and tables over prose
- **Imperative** - "Use X" not "You should use X"
- **Specific** - "Run `task build`" not "build the project"
- **Stable** - Only include patterns that rarely change

## Plugin CLAUDE.md

Each plugin in `plugins/` should have its own CLAUDE.md with:

1. One-line description
2. Installation instructions
3. Usage instructions
4. CLI reference (if applicable)
5. Architecture overview

## Validation

Before updating CLAUDE.md:

1. Is this a permanent project convention? -> Add
2. Is this session-specific? -> Skip
3. Is this a one-time note? -> Skip
