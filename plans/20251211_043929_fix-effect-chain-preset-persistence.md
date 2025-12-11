# Plan: Fix Effect Chain Preset Persistence Bug

## Problem

Preset selections in the effect chain (volume/tunnel/frequency) were not being remembered when switching between categories.

## Root Cause

The filename wasn't being reliably passed to backend endpoints because:
1. Template used `{% if current_filename %}` conditional which depended on server context
2. After HTMX swaps, the server might not have the filename in context

## Solution

Use HTMX's `hx-vals="js:{...}"` feature to always pass the filename from JavaScript's global state:

1. Made `currentFilename` global by using `window.currentFilename`
2. Added `hx-vals="js:{filename: window.currentFilename || ''}"` to all HTMX elements
3. Removed conditional `{% if current_filename %}?filename={{ current_filename }}{% endif %}` from URLs

## Files Modified

| File | Change |
|------|--------|
| `app/templates/index.html` | Changed `var currentFilename` to `window.currentFilename` |
| `app/templates/partials/effect_chain_accordion.html` | Added `hx-vals` to all headers and preset buttons, removed conditional filename from URLs |

## TODO List (Completed)

- [x] Make currentFilename global (window.currentFilename)
- [x] Add hx-vals to accordion headers
- [x] Add hx-vals to all preset buttons
- [x] Remove conditional filename from URLs
- [x] Test preset persistence
