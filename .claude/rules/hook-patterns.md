# Hook Patterns

Standards for hook configuration aligned with official Claude Code patterns.

## hooks.json Structure

### Plugin Format (with wrapper)

For `plugins/*/hooks/hooks.json`:

```json
{
  "description": "Brief explanation of hooks purpose",
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

Key points:
- Top-level `description` field is recommended
- `hooks` wrapper object is required
- Event types nested inside `hooks`

### Settings Format (direct)

For `.claude/settings.json` hooks (user settings):

```json
{
  "PreToolUse": [...],
  "PostToolUse": [...]
}
```

Key points:
- No wrapper - events at top level
- No description field
- This is for user/project settings only

## Matcher Patterns

### Exact Match

```json
"matcher": "Write"
```

### Multiple Tools

```json
"matcher": "Read|Write|Edit"
```

### Wildcard (All)

```json
"matcher": "*"
```

### Regex Patterns

```json
"matcher": "mcp__.*__delete.*"
```

### Common Patterns

| Pattern | Matches |
|---------|---------|
| `*` | All tools |
| `Read\|Write\|Edit` | File operations |
| `Bash` | Shell commands |
| `mcp__.*` | All MCP tools |
| `mcp__plugin_name_.*` | Plugin's MCP tools |

## Timeout Standards

| Hook Type | Default | Recommended |
|-----------|---------|-------------|
| Command (fast) | 60s | 5-10s |
| Command (complex) | 60s | 30-60s |
| Prompt | 30s | 30s |

Always set explicit timeouts:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 10
}
```

## Path Conventions

### Always Use ${CLAUDE_PLUGIN_ROOT}

```json
{
  "type": "command",
  "command": "uv run ${CLAUDE_PLUGIN_ROOT}/hooks/wrapper.py pre_tool"
}
```

Never use relative or hardcoded paths:

```json
// BAD
"command": "bash ./hooks/script.sh"
"command": "bash /home/user/plugins/hook.sh"

// GOOD
"command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/script.sh"
```

## Hook Type Selection

### Prompt-Based Hooks

Use for context-aware decisions:

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this tool use is appropriate: $TOOL_INPUT",
  "timeout": 30
}
```

Supported events: Stop, SubagentStop, UserPromptSubmit, PreToolUse

### Command Hooks

Use for deterministic checks:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 10
}
```

Use for:
- Fast validation
- File system operations
- External tool integration
- Performance-critical checks

## JSON Contract

### Input Format (stdin)

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {}
}
```

### Output Format (stdout)

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

### PreToolUse Decision Output

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {}
  },
  "systemMessage": "Explanation"
}
```

### Stop Decision Output

```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

## Event Reference

| Event | When | Use For |
|-------|------|---------|
| PreToolUse | Before tool | Validation, modification |
| PostToolUse | After tool | Feedback, logging |
| Stop | Agent stopping | Completeness check |
| SubagentStop | Subagent done | Task validation |
| SessionStart | Session begins | Context loading |
| SessionEnd | Session ends | Cleanup |
| UserPromptSubmit | User input | Context, validation |
| PreCompact | Before compact | Preserve context |
| Notification | User notified | Logging |

## Validation Checklist

- [ ] Top-level `description` field present
- [ ] `hooks` wrapper object used
- [ ] All paths use `${CLAUDE_PLUGIN_ROOT}`
- [ ] Timeouts explicitly set
- [ ] Matchers are valid patterns
- [ ] Event types are recognized
- [ ] Scripts referenced exist
- [ ] JSON output is valid
