# Plan: Preset Chaining, CRT Preset, and Processing Progress Modal

**Affects:** `/workspace/app/models.py`, `/workspace/app/routers/audio.py`, `/workspace/app/services/processor.py`, `/workspace/app/services/file_metadata.py`, `/workspace/app/services/settings.py`, `/workspace/app/services/filters_video.py`, `/workspace/presets_themes.yml`, `/workspace/app/templates/partials/`

---

## Feature Summary

| Feature | Description |
|---------|-------------|
| CRT Playback Preset | True 240p (320x240) 4:3 output for CRT television |
| Preset Chaining | Select multiple presets in order with (1), (2) badges |
| Processing Progress Modal | Centered popup with progress bar, ETA, FFmpeg log |

---

## Feature 1: CRT Playback Preset

### Implementation

**File: `/workspace/app/services/filters_video.py`**

Add scale filter function:
```python
def build_scale_filter(width: int, height: int) -> str:
    """Build scale filter for resolution change."""
    if width <= 0 or height <= 0:
        return ""
    return f"scale={width}:{height}"
```

**File: `/workspace/presets_themes.yml`**

Add new preset:
```yaml
video:
  crt_playback:
    name: "CRT Playback"
    description: "True 240p 4:3 for CRT television"
    icon: "fa-tv"
    filters:
      - type: crop
        params:
          aspect_ratio: "4:3"
      - type: scale
        params:
          width: 320
          height: 240
      - type: blur
        params:
          sigma: 0.3
```

**Files to update:**
- `filter_chain.py`: Add `scale_width`, `scale_height` parameters
- `audio.py`: Extract and pass scale values
- `file_metadata.py`: Add `scale` to default settings
- `models.py`: Add `scale` CategorySettings to UserSettings

---

## Feature 2: Preset Chaining

### Data Model Changes

**File: `/workspace/app/models.py`**

Replace single theme tracking with ordered chains:
```python
class UserSettings(BaseModel):
    # ... existing fields ...
    # Replace these:
    # applied_video_theme: str = ""
    # applied_audio_theme: str = ""

    # With ordered chains:
    video_theme_chain: list[str] = []
    audio_theme_chain: list[str] = []
```

### Persistence Changes

**File: `/workspace/app/services/file_metadata.py`**

Update defaults:
```python
def get_default_settings() -> dict[str, Any]:
    return {
        # ... existing ...
        "video_theme_chain": [],
        "audio_theme_chain": [],
    }
```

Add chain management functions:
```python
def toggle_theme_in_chain(filename: str, media_type: str, preset_key: str) -> list[str]:
    """Toggle preset in chain - add if not present, remove if present."""

def clear_theme_chain(filename: str, media_type: str) -> list[str]:
    """Clear all presets from chain."""
```

### Filter Application Logic

**File: `/workspace/app/routers/audio.py`**

Replace `apply_theme_preset` with `toggle_theme_preset`:
```python
@router.post("/toggle-theme-preset/{media_type}/{preset_key}")
async def toggle_theme_preset(...):
    """Toggle preset in chain - add if not present, remove if present."""
    chain = get_theme_chain(filename, media_type)

    if preset_key == "none":
        # Clear entire chain
        chain = []
    elif preset_key in chain:
        chain.remove(preset_key)
    else:
        chain.append(preset_key)

    # Apply all presets in order (last wins for conflicts)
    clear_all_custom_values(media_type, filename)
    for key in chain:
        preset = get_theme_preset(media_type, key)
        for filter_step in preset.filters:
            update_category_custom_values(filter_step.type, filter_step.params, filename)

    save_theme_chain(filename, media_type, chain)
```

### UI Changes

**File: `/workspace/app/templates/partials/filters_presets_accordion.html`**

Add chain position badge:
```html
<div class="preset-card {% if preset_key in chain %}preset-card--selected{% endif %}">
    {% if preset_key in chain %}
    <span class="preset-chain-badge">{{ chain.index(preset_key) + 1 }}</span>
    {% endif %}
    <!-- existing card content -->
</div>
```

**File: `/workspace/app/static/css/filter-chain.css`**

Add badge styles:
```css
.preset-chain-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    background: var(--accent);
    color: var(--bg-primary);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 12px;
    z-index: 1;
}

.preset-card {
    position: relative;  /* Ensure badge positions correctly */
}
```

---

## Feature 3: Processing Progress Modal

### Backend: SSE Progress Streaming

**File: `/workspace/app/services/processor.py`**

Add progress generator function:
```python
import re
from typing import Generator

def process_video_with_progress(
    input_file: Path,
    start_time: str,
    end_time: str,
    audio_filter: str | None,
    video_filter: str | None,
    total_duration_ms: int,
) -> Generator[dict, None, Path]:
    """Process video with progress updates via generator."""

    cmd = [..., "-progress", "pipe:1", ...]  # FFmpeg progress to stdout

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    for line in process.stdout:
        if line.startswith("out_time_ms="):
            current_ms = int(line.split("=")[1])
            percent = min(100, (current_ms / total_duration_ms) * 100)
            yield {
                "type": "progress",
                "percent": percent,
                "current_ms": current_ms,
                "total_ms": total_duration_ms,
            }
        elif line.startswith("progress=end"):
            yield {"type": "complete"}

    process.wait()
    return output_path
```

### SSE Endpoint

**File: `/workspace/app/routers/audio.py`**

Add SSE endpoint:
```python
from sse_starlette.sse import EventSourceResponse

@router.post("/process-with-progress")
async def process_with_progress(request: Request, ...):
    """Process with SSE progress streaming."""

    async def event_generator():
        for update in process_video_with_progress(...):
            yield {
                "event": update["type"],
                "data": json.dumps(update)
            }

    return EventSourceResponse(event_generator())
```

### Frontend Modal

**File: `/workspace/app/templates/partials/processing_modal.html`** (new file)

```html
<div id="processing-modal" class="modal-backdrop active">
  <div class="modal processing-modal">
    <div class="modal-header">
      <h3>Processing Video</h3>
    </div>
    <div class="modal-body">
      <!-- Current step -->
      <div class="processing-step">
        <span id="current-step">Initializing...</span>
      </div>

      <!-- Progress bar -->
      <div class="progress-container">
        <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
        <span class="progress-text" id="progress-text">0%</span>
      </div>

      <!-- Time info -->
      <div class="processing-time">
        <span>Elapsed: <span id="elapsed-time">0:00</span></span>
        <span>ETA: <span id="eta-time">Calculating...</span></span>
      </div>

      <!-- FFmpeg output log -->
      <div class="ffmpeg-log-container">
        <div class="ffmpeg-log" id="ffmpeg-log"></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="cancelProcessing()">Cancel</button>
    </div>
  </div>
</div>

<script>
let startTime = Date.now();
const eventSource = new EventSource('/process-with-progress?...');

eventSource.addEventListener('progress', (e) => {
  const data = JSON.parse(e.data);
  document.getElementById('progress-bar').style.width = data.percent + '%';
  document.getElementById('progress-text').textContent = Math.round(data.percent) + '%';

  // Calculate ETA
  const elapsed = (Date.now() - startTime) / 1000;
  const rate = data.percent / elapsed;
  const remaining = (100 - data.percent) / rate;
  document.getElementById('elapsed-time').textContent = formatTime(elapsed);
  document.getElementById('eta-time').textContent = formatTime(remaining);
});

eventSource.addEventListener('log', (e) => {
  const log = document.getElementById('ffmpeg-log');
  log.textContent += e.data + '\n';
  log.scrollTop = log.scrollHeight;
});

eventSource.addEventListener('complete', (e) => {
  closeModal();
  htmx.trigger('#history-panel', 'refresh');
});

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
</script>
```

### CSS Styles

**File: `/workspace/app/static/css/modal.css`**

Add to existing modal styles:
```css
.processing-modal {
    max-width: 500px;
}

.processing-step {
    margin-bottom: 16px;
    font-weight: 500;
}

.progress-container {
    background: var(--bg-tertiary);
    border-radius: 4px;
    height: 24px;
    position: relative;
    overflow: hidden;
}

.progress-bar {
    background: var(--accent);
    height: 100%;
    transition: width 0.3s ease;
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-weight: bold;
}

.ffmpeg-log-container {
    margin-top: 16px;
    max-height: 150px;
    overflow-y: auto;
    background: var(--bg-secondary);
    border-radius: 4px;
    padding: 8px;
}

.ffmpeg-log {
    font-family: monospace;
    font-size: 11px;
    white-space: pre-wrap;
    color: var(--text-secondary);
}

.processing-time {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    font-size: 13px;
    color: var(--text-secondary);
}
```

---

## Dependencies

**File: `/workspace/pyproject.toml`**

Add SSE library:
```toml
dependencies = [
    # ... existing ...
    "sse-starlette>=2.0.0",
]
```

---

## Implementation Order

1. **CRT Playback Preset** (simplest, standalone)
   - Add scale filter function
   - Add to presets_themes.yml
   - Wire through filter chain
   - Test with 4:3 240p output

2. **Preset Chaining** (medium complexity)
   - Update data models (chains instead of single)
   - Add chain management functions
   - Update endpoint to toggle behavior
   - Add UI badges with numbers
   - Test chain ordering and "last wins"

3. **Processing Progress Modal** (most complex)
   - Add sse-starlette dependency
   - Refactor processor for streaming with Popen
   - Add SSE endpoint
   - Create modal template
   - Add JavaScript event handling
   - Test progress updates and ETA

---

## Verification

1. `task rebuild`
2. Open http://localhost:8000
3. **CRT Preset**: Apply "CRT Playback" → Verify output is 320x240 4:3
4. **Chaining**: Click VHS → shows (1), click Security Cam → shows (2)
5. **Chaining conflicts**: Both have contrast → Security Cam's 1.5 wins over VHS's 1.2
6. **Toggle off**: Click VHS again → removed from chain, Security Cam becomes (1)
7. **Progress Modal**: Click Process → Modal appears with progress bar
8. **Modal details**: Progress bar moves, ETA updates, FFmpeg log scrolls
9. **Completion**: Modal closes automatically, history refreshes

---

## Files to Modify

| File | Changes |
|------|---------|
| `pyproject.toml` | Add sse-starlette dependency |
| `app/services/filters_video.py` | Add `build_scale_filter()` |
| `app/services/filter_chain.py` | Add scale_width, scale_height params |
| `app/models.py` | Add scale CategorySettings, change theme to chains |
| `app/services/file_metadata.py` | Add scale defaults, chain functions |
| `app/services/settings.py` | Add chain management, update loaders |
| `app/routers/audio.py` | Add toggle endpoint, SSE endpoint |
| `app/services/processor.py` | Add `process_video_with_progress()` |
| `presets_themes.yml` | Add CRT Playback preset |
| `app/templates/partials/filters_presets_accordion.html` | Add chain badges |
| `app/templates/partials/processing_modal.html` | New file |
| `app/static/css/filter-chain.css` | Badge styles |
| `app/static/css/modal.css` | Progress modal styles |
| `app/main.py` | Update template context for chain attributes |

---

## Execution Notes

**Deviations from original plan:**
- `app/main.py` required updating: lines 240-241 referenced deprecated `applied_video_theme`/`applied_audio_theme` attributes instead of new `video_theme_chain`/`audio_theme_chain`

**Issues discovered:**
- 500 Internal Server Error on first test due to AttributeError in main.py

**Additional work completed:**
- Fixed main.py template context to use chain attributes
