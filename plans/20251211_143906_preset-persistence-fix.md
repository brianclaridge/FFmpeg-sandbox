# Plan: Fix Effect Chain Preset Persistence Bug

## Problem Statement

Effect chain preset selections (volume/tunnel/frequency) are not persisting to YAML or UI after selection. Previous fix attempts added `hx-vals` to templates but did not address the backend issue.

## Root Cause Analysis

**Location:** `app/routers/audio.py` lines 379 and 401

**Issue:** The `filename` parameter lacks `Form()` annotation. FastAPI's default behavior for POST endpoints without `Form()` is to look for query parameters, not form data. HTMX sends filename in the POST body via `hx-vals`, so FastAPI never receives it.

**Flow Breakdown:**

```
HTMX sends:  POST /partials/accordion-preset/volume/2x
             Body: filename=myfile.mp4

FastAPI receives: category="volume", preset="2x", filename=None  ← BUG

settings.py: if not filename: return early WITHOUT persisting
```

**Evidence:**
- YAML files ARE being created (`.data/input/tw-547926855.yml` exists)
- Persistence mechanism works when `filename` is provided
- History entries ARE saved (shows persistence layer is functional)
- The `filename=None` causes early return in `update_category_preset()` at line 40

## Solution

Add `Form()` annotation to receive filename from POST body instead of query params.

### Files to Modify

| File | Line | Change |
|------|------|--------|
| `app/routers/audio.py` | 401 | `filename: str \| None = None` → `filename: str = Form("")` |
| `app/routers/audio.py` | 379 | `filename: str \| None = None` → `filename: str = Form("")` |

### Required Import

Ensure `Form` is imported from `fastapi`:
```python
from fastapi import Form  # Add if not present
```

## Phase 1: Playwright Verification (Pre-Fix)

Use browser automation to confirm the bug exists:

1. Navigate to http://localhost:8000
2. Take page snapshot
3. Select file from "Source File" dropdown (e.g., tw-547926855.mp4)
4. Click "Tunnel" header to expand
5. Click "Medium" preset button
6. **Capture network request** - verify POST body contains `filename=...`
7. Switch to Volume, then back to Tunnel
8. Check if preset persisted or reverted

**Expected finding:** `filename` may be in POST body but FastAPI doesn't receive it (missing `Form()`)

## Phase 2: Apply Fix

1. Update `app/routers/audio.py` line 401:
   ```python
   async def set_accordion_preset(..., filename: str = Form("")):
   ```
2. Update line 379 (legacy endpoint) similarly

## Phase 3: Playwright Verification (Post-Fix)

Repeat Phase 1 steps to confirm:
- Preset selection persists after category switch
- YAML file updates with new preset value

## TODO List

- [ ] **Phase 1:** Run Playwright to capture network requests (pre-fix baseline)
- [ ] **Phase 2:** Add `Form("")` to `set_accordion_preset()` line 401
- [ ] **Phase 2:** Add `Form("")` to `set_category_preset()` line 379
- [ ] **Phase 3:** Run Playwright to verify fix works
- [ ] **Phase 3:** Check YAML file shows updated preset

## Risk Assessment

**Low risk:** This is a targeted 2-line fix. The `Form("")` default allows empty string when no file selected, matching existing behavior where `if not filename:` returns defaults.
