# Plan: Fix History Apply and Video Playback

**Affects:** `/workspace/app/templates/partials/history_preview.html`, `/workspace/app/routers/history.py`

---

## Issue Summary

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Apply doesn't restore presets | Wrong template path, incomplete context | Fix template + add missing context |
| Video plays as audio | Always uses `<audio>` element | Add media type detection |

---

## Fix 1: Video Playback

**File:** `/workspace/app/templates/partials/history_preview.html`

**Current:**
```html
<audio controls autoplay>
    <source src="/preview/{{ entry.output_file }}" type="audio/mpeg">
</audio>
```

**Fixed:**
```html
{% set is_video = entry.output_file.endswith(('.mp4', '.webm', '.mkv')) %}
{% if is_video %}
<video controls autoplay loop class="output-video">
    <source src="/preview/{{ entry.output_file }}" type="video/mp4">
</video>
{% else %}
<audio controls autoplay>
    <source src="/preview/{{ entry.output_file }}" type="audio/mpeg">
</audio>
{% endif %}
```

---

## Fix 2: Apply Button Template + Context

**File:** `/workspace/app/routers/history.py`

### Problem 1: Wrong template path (line 100)
```python
# Current (broken - template doesn't exist):
return templates.TemplateResponse("partials/effect_chain_accordion.html", context)

# Fixed:
return templates.TemplateResponse("partials/filters_tabs.html", context)
```

### Problem 2: Missing imports and context
The `filters_tabs.html` template requires more context than `_get_accordion_context()` provides. Need to:
1. Import all preset getters (video presets, theme presets)
2. Build complete context matching what `/partials/filter-chain` endpoint provides

**Required imports to add:**
```python
from app.services.presets import (
    get_volume_presets, get_tunnel_presets, get_frequency_presets,
    get_speed_presets, get_pitch_presets, get_noise_reduction_presets,
    get_compressor_presets, get_brightness_presets, get_contrast_presets,
    get_saturation_presets, get_blur_presets, get_sharpen_presets,
    get_transform_presets,
)
from app.services.presets_themes import get_video_theme_presets, get_audio_theme_presets
```

**Required context additions:**
- All 13 filter category presets and current values
- Theme presets (video_theme_presets, audio_theme_presets)
- Theme chains (video_theme_chain, audio_theme_chain)

### Approach: Import audio.py's _get_accordion_context()

The `_get_accordion_context` in audio.py is complete (all 13 filter categories).
Import and use it instead of the incomplete one in history.py.

**Changes to history.py:**

```python
# Remove local _get_accordion_context() and import from audio.py
from app.routers.audio import _get_accordion_context
from app.services.presets_themes import get_video_theme_presets, get_audio_theme_presets

# In apply_history endpoint:
context = _get_accordion_context(user_settings, filename)
context["request"] = request
context["video_theme_presets"] = get_video_theme_presets()
context["audio_theme_presets"] = get_audio_theme_presets()
return templates.TemplateResponse("partials/filters_tabs.html", context)
```

---

## Implementation Steps

1. Fix `history_preview.html` - Add video/audio detection
2. Update `history.py`:
   - Import `_get_accordion_context` from `audio.py`
   - Import theme preset functions
   - Remove local `_get_accordion_context()` function
   - Fix template path to `filters_tabs.html`
   - Add theme presets to context

---

## Verification

1. `task rebuild`
2. Upload a video file, apply filters, process as MP4
3. In history: click preview → should show video player (not audio)
4. Click Apply → filter tabs should render with restored settings
5. Upload audio file, process as MP3
6. In history: click preview → should show audio player
7. Click Apply → filter tabs should render correctly
