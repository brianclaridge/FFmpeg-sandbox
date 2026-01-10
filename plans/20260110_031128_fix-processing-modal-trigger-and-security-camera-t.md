# Plan: Fix Processing Modal Trigger and Security Camera Timer

**Affects:** `/workspace/app/templates/index.html`, `/workspace/app/services/filters_video.py`

---

## Issue Summary

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Processing modal not showing | Process button uses HTMX sync endpoint, never calls `startProcessingWithProgress()` | Wire button to call modal function |
| Security camera timer missing | Strftime colons over-escaped (`\:` instead of `:`) | Remove escaping from time format colons |

---

## Fix 1: Security Camera Timer

**File:** `/workspace/app/services/filters_video.py` (lines 72-74)

**Current (broken):**
```python
"text='%{localtime\\:%Y-%m-%d %H\\:%M\\:%S}':"
```

**Fixed:**
```python
"text='%{localtime\\:%Y-%m-%d %H:%M:%S}':"
```

**Explanation:**
- The `\\:` after `localtime` is correct (FFmpeg separator)
- The `\\:` in `%H\\:%M\\:%S` is wrong - strftime needs literal colons
- Over-escaping causes strftime to fail, truncating or omitting the time portion

---

## Fix 2: Processing Modal Trigger

**File:** `/workspace/app/templates/index.html`

### Current Flow (broken):
1. User clicks Process button
2. Form submits via HTMX to `/process` (synchronous)
3. Page waits, then swaps result into `#preview-area`
4. Modal never shown

### Fixed Flow:
1. User clicks Process button
2. JavaScript intercepts, extracts form values
3. Calls `startProcessingWithProgress(inputFile, startTime, endTime, outputFormat)`
4. Modal shows with SSE progress streaming
5. On complete, modal closes and refreshes history

### Implementation (Option A: onclick handler)

**Step 1:** Change button (line ~127):
```html
<button type="button" class="btn-primary" onclick="triggerProcessWithProgress()">
    <span class="btn-text">Process</span>
</button>
```

**Step 2:** Add JavaScript function (in script section):
```javascript
function triggerProcessWithProgress() {
    const form = document.getElementById('process-form');
    const inputFile = form.querySelector('[name="input_file"]')?.value;
    const startTime = document.getElementById('start-time')?.value || '00:00:00';
    const endTime = document.getElementById('end-time')?.value || '00:00:06';
    const outputFormat = form.querySelector('[name="output_format"]')?.value || 'mp4';

    if (!inputFile) {
        alert('Please select a file first');
        return;
    }

    // Stop any active preview
    if (typeof ClipRangeController !== 'undefined') {
        ClipRangeController.stopPreview();
        ClipRangeController.stopVideoPreview();
    }

    startProcessingWithProgress(inputFile, startTime, endTime, outputFormat);
}
```

---

## Verification

1. `task rebuild`
2. Upload a video file
3. **Security Camera Test:** Apply Security Cam preset → Process → Verify timestamp shows `YYYY-MM-DD HH:MM:SS` (not just date)
4. **Modal Test:** Click Process → Verify modal appears with progress bar → Progress updates → Modal closes on complete

---

## Files to Modify

| File | Change |
|------|--------|
| `app/services/filters_video.py` | Remove `\\:` escaping from strftime time portion |
| `app/templates/index.html` | Add `triggerProcessWithProgress()` function and wire to button |
