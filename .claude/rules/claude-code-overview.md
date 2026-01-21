# Claude Code Overview

> Claude Code -- Anthropic's agentic CLI -- An AI-powered terminal assistant for software engineering with tool use, MCP servers, and custom agents.

**Claude Code** is the foundation of your orchestration layer. Rules in `.claude/rules/` shape agent behavior; agents in `.claude/agents/` define specialized sub-agents.

## This Repository

This is a **plugin monorepo** for Claude Code plugins. Key paths:

| Path | Purpose |
| ---- | ------- |
| `plugins/` | Plugin source directories |
| `.claude/agents/` | Specialized sub-agents |
| `.claude/rules/` | Behavior rules (this file) |
| `tasks/` | Taskfile includes |

## Agents

See `.claude/agents/` for available sub-agents:

- **rust-maintainer** - Rust code quality, cross-platform builds
- **python-maintainer** - Python scripts, PEP 723, hooks
- **hook-validator** - Hook configuration, event handling
- **plugin-tester** - E2E testing, plugin validation
- **plugin-manifest** - plugin.json validation
- **skill-author** - SKILL.md creation and quality
- **release-manager** - Versioning, changelogs, releases

## Resources

- [docs](https://docs.anthropic.com/en/docs/claude-code)
- [sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [memory](https://docs.anthropic.com/en/docs/claude-code/memory)
- [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
