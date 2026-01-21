# Chrome Browser Automation

## When to Use

Use Chrome automation for:
- **Visual testing** - Verify UI renders correctly after changes
- **Debugging** - Inspect console errors, network requests, DOM state
- **Form testing** - Test input validation, submissions, error states
- **Recording demos** - Create GIFs showing feature workflows

Do NOT use for:
- Tasks that can be done via CLI or API
- Automated scraping or data collection
- Actions requiring login credentials

## Available Capabilities

| Tool | Purpose |
|------|---------|
| `tabs_context_mcp` | Get current tabs (call first!) |
| `tabs_create_mcp` | Create new tab |
| `navigate` | Go to URL or back/forward |
| `read_page` | Get accessibility tree of elements |
| `find` | Find elements by natural language |
| `computer` | Click, type, screenshot, scroll |
| `javascript_tool` | Execute JS in page context |
| `read_console_messages` | Read console output |
| `read_network_requests` | Inspect XHR/fetch calls |
| `gif_creator` | Record browser interactions |

## Tab Management

**Always call `tabs_context_mcp` first** to get available tabs.

```
1. Call tabs_context_mcp to see existing tabs
2. Create fresh tab with tabs_create_mcp (don't reuse old tabs)
3. Navigate to target URL
4. Perform actions
```

## Debugging Workflows

### Check for JavaScript Errors
```
1. Navigate to page
2. read_console_messages with pattern: "error|Error|exception"
3. Report findings
```

### Inspect Network Requests
```
1. Navigate to page (requests are captured)
2. read_network_requests with urlPattern: "/api/"
3. Check status codes and response times
```

### Verify UI State
```
1. Take screenshot with computer action: "screenshot"
2. Use read_page to get element tree
3. Use find to locate specific elements by description
```

## Recording GIFs

For multi-step workflows worth documenting:

```
1. gif_creator action: "start_recording"
2. Take initial screenshot
3. Perform actions (each gets captured)
4. Take final screenshot
5. gif_creator action: "stop_recording"
6. gif_creator action: "export" with download: true
```

Name GIFs meaningfully: `login_flow.gif`, `filter_preview.gif`

## Best Practices

- **Filter console output** - Always use `pattern` parameter to avoid noise
- **Handle modals carefully** - Avoid triggering alert/confirm dialogs (they block)
- **Keep browser visible** - Don't minimize; screenshots need visible viewport
- **Use element refs** - After `read_page`, use `ref` parameter for precise clicks
- **Wait after navigation** - Use `computer` with `action: "wait"` for dynamic content

## Avoid

- Clicking elements that trigger `alert()`, `confirm()`, `prompt()`
- Entering passwords or sensitive credentials
- Creating accounts on behalf of user
- Downloading files without explicit permission
- Rabbit-holing on failed actions (ask user after 2-3 attempts)
