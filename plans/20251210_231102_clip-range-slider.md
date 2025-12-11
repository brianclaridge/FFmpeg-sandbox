# Clip Range Slider + Viewport Centering

## Goals
1. Add dual-handle range slider above Start/End fields for clip selection
2. Fetch file duration when file is selected (dropdown, upload, or URL download)
3. Sync sliders bidirectionally with text fields (millisecond precision)
4. Auto-play preview on loop when sliders are adjusted
5. Center app area horizontally and vertically in viewport

## Implementation

### Phase 1: Backend - Duration Detection

**`app/services/processor.py`** - Add function:
```python
def get_file_duration(file_path: Path) -> int | None:
    """Get duration in milliseconds using ffprobe."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        return int(float(result.stdout.strip()) * 1000)
    return None
```

**`app/routers/audio.py`** - Add endpoints:
- `GET /duration/{filename}` → Returns `{duration_ms, duration_formatted}`
- `GET /clip-preview?filename=&start=&end=` → Streams MP3 clip for preview

### Phase 2: Frontend - Dual Range Slider

**`app/templates/index.html`** - Add above Start/End row:
- Two overlapping `<input type="range">` (start=green, end=accent)
- Labels showing `HH:MM:SS.mmm` for start/end and clip duration
- Hidden `<audio id="clip-preview-audio" loop>` for playback
- `ClipRangeController` JS class handling:
  - Bidirectional sync between sliders and text fields
  - Collision prevention (min 100ms clip)
  - Debounced preview trigger on slider release
  - Duration fetch on file selection

### Phase 3: CSS Updates

**`app/static/css/styles.css`**:
- Dual-range slider styles (overlapping inputs, fill bar between handles)
- Start thumb: `var(--success)`, End thumb: `var(--accent)`
- Viewport centering: `body { display: flex }`, `.container { justify-content: center }`
- Media query fallback for small viewports

### Phase 4: Integration Triggers

**`app/templates/partials/upload_status.html`**:
- After updating dropdown, call `ClipRangeController.fetchDuration(filename)`

**`app/templates/partials/download_complete.html`**:
- After OOB swap, call `ClipRangeController.fetchDuration(filename)`

## Files to Modify

| File | Changes |
|------|---------|
| `app/services/processor.py` | Add `get_file_duration()` |
| `app/routers/audio.py` | Add `/duration/{filename}`, `/clip-preview` endpoints |
| `app/templates/index.html` | Add slider HTML, audio element, ClipRangeController JS |
| `app/static/css/styles.css` | Dual-range CSS, viewport centering |
| `app/templates/partials/upload_status.html` | Trigger duration fetch |
| `app/templates/partials/download_complete.html` | Trigger duration fetch |

## TODOs

1. [ ] Add `get_file_duration()` to processor.py
2. [ ] Add `/duration/{filename}` endpoint to audio.py
3. [ ] Add `/clip-preview` endpoint to audio.py
4. [ ] Add dual-range slider HTML to index.html
5. [ ] Add ClipRangeController JS to index.html
6. [ ] Add dual-range slider CSS to styles.css
7. [ ] Add viewport centering CSS to styles.css
8. [ ] Update upload_status.html to trigger duration fetch
9. [ ] Update download_complete.html to trigger duration fetch
10. [ ] Rebuild and test
