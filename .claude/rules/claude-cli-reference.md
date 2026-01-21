# Claude CLI Reference

> claude -- AI-Powered Development Assistant -- Interactive terminal session with Claude AI for code generation, debugging, and task automation.

**claude** is the CLI interface for Claude Code. Use interactive mode by default, `--print` for scripted workflows.

## Core Usage

| Pattern | Purpose |
| ------- | ------- |
| `claude` | Start interactive session |
| `claude "prompt"` | Interactive session with initial prompt |
| `claude -p "prompt"` | Non-interactive output (pipes, scripts) |
| `claude -c` | Continue most recent session in current directory |
| `claude -r [term]` | Resume session by ID or search term |

## Session Management

| Flag | Purpose |
| ---- | ------- |
| `--continue, -c` | Resume most recent conversation |
| `--resume [value], -r` | Resume by session ID or picker |
| `--session-id <uuid>` | Use specific session ID |
| `--fork-session` | Create new ID when resuming (with -r/-c) |
| `--no-session-persistence` | Disable session saving (with -p) |

## Model & Agent Control

| Flag | Purpose |
| ---- | ------- |
| `--model <model>` | Override model (alias or full name) |
| `--agent <agent>` | Override agent for session |
| `--agents <json>` | Define custom agents |
| `--fallback-model <model>` | Auto-fallback when overloaded (with -p) |

## Tool Management

| Flag | Purpose |
| ---- | ------- |
| `--tools <tools>` | Specify available tools ("" disables, "default" all) |
| `--allowedTools <tools>` | Comma/space-separated whitelist |
| `--disallowedTools <tools>` | Comma/space-separated blocklist |
| `--disable-slash-commands` | Disable all skills |

## Permissions

| Flag | Purpose |
| ---- | ------- |
| `--permission-mode <mode>` | Set permission mode (acceptEdits, bypassPermissions, default, delegate, dontAsk, plan) |
| `--dangerously-skip-permissions` | Bypass all permission checks (sandbox only) |
| `--allow-dangerously-skip-permissions` | Enable bypass as option (not default) |

## MCP Integration

| Flag | Purpose |
| ---- | ------- |
| `--mcp-config <configs>` | Load MCP servers from JSON files/strings |
| `--strict-mcp-config` | Only use --mcp-config servers |
| `--chrome` | Enable Claude in Chrome integration |
| `--no-chrome` | Disable Claude in Chrome |
| `--ide` | Auto-connect to IDE if available |

## Output Control

| Flag | Purpose |
| ---- | ------- |
| `--print, -p` | Non-interactive output mode |
| `--output-format <format>` | text (default), json, stream-json (with -p) |
| `--input-format <format>` | text (default), stream-json (with -p) |
| `--include-partial-messages` | Stream partial chunks (with -p and stream-json) |
| `--replay-user-messages` | Re-emit user messages (with stream-json) |

## Advanced

| Flag | Purpose |
| ---- | ------- |
| `--add-dir <dirs>` | Grant tool access to additional directories |
| `--system-prompt <prompt>` | Override system prompt |
| `--append-system-prompt <prompt>` | Append to system prompt |
| `--json-schema <schema>` | Validate structured output |
| `--max-budget-usd <amount>` | Cap API spending (with -p) |
| `--settings <file-or-json>` | Load additional settings |
| `--setting-sources <sources>` | Filter setting sources (user, project, local) |
| `--plugin-dir <paths>` | Load plugins from directories |
| `--betas <betas>` | Include beta headers (API key users) |
| `--debug [filter], -d` | Enable debug mode with optional category filter |
| `--verbose` | Override verbose mode setting |

## Commands

| Command | Purpose |
| ------- | ------- |
| `claude doctor` | Check auto-updater health |
| `claude install [target]` | Install native build (stable, latest, or version) |
| `claude mcp` | Configure and manage MCP servers |
| `claude plugin` | Manage plugins |
| `claude setup-token` | Set up long-lived auth token (subscription required) |
| `claude update` | Check and install updates |

## Common Patterns

**This repo:**

```bash
task claude  # Launch with Opus, Chrome, IDE integrations
```

**Interactive with custom model:**

```bash
claude --model opus
```

**Pipe output:**

```bash
echo "analyze this code" | claude -p --output-format json
```

**Continue last session:**

```bash
claude -c
```

**Load plugin from this repo:**

```bash
claude --plugin-dir ./plugins/control-freak
```

## Resources

- [claude.ai/code](https://claude.ai/code)
- [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
