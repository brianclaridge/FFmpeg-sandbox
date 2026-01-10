# Plan: Fix History Column Overflow

**Affects:** `/workspace/app/static/css/layout.css`

---

## Problem

After removing the hardcoded `max-height: 300px` from `.history-list`, the history column now overflows beyond available viewport space without showing scrollbars.

## Root Cause

The flex layout chain is broken at the `main` element:

```
body (height: 100vh, overflow: hidden)
└── .container (flex column, height: 100%)
    ├── header (flex-shrink: 0)
    └── main (NO STYLES - breaks layout)
        └── form (no styles)
            └── .grid-4 (flex: 1, min-height: 0)
                └── .card (overflow-y: auto, min-height: 0)
```

The `main` element needs to:
1. Fill remaining space (`flex: 1`)
2. Allow shrinking (`min-height: 0`)
3. Contain overflow (`overflow: hidden`)
4. Pass height to children (`display: flex`)

## Implementation

**File:** `/workspace/app/static/css/layout.css`

Add after header styles (around line 60):

```css
/* Main content area */
main {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

main > form {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
}
```

## Verification

1. `task rebuild`
2. Open http://localhost:8000
3. Add multiple history entries (process several files)
4. Verify history column shows scrollbar when content exceeds viewport
5. Verify other columns maintain proper sizing
