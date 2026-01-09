# Plan: Theme Preset UX Enhancements

**Affects:** `/workspace/presets_themes.yml`, `/workspace/app/templates/partials/filters_presets_accordion.html`, `/workspace/app/static/css/filter-chain.css`, `/workspace/app/routers/audio.py`, `/workspace/app/services/settings.py`, `/workspace/app/services/file_metadata.py`

---

## Requirements

1. **"None" preset** - Add default option to unapply/clear current theme preset
2. **Combine video + audio** - Allow selecting one video preset AND one audio preset together
3. **Visual selected state** - Distinct from hover; shows which preset(s) are currently applied

---

## Current State

- Theme presets apply filters via `custom_values` storage (preset="custom")
- No tracking of which theme preset was applied (only "custom" flag)
- No visual indication of currently applied preset
- Clicking a new preset replaces current (no explicit "none/clear" option)

---

## Implementation

### Step 1: Track Applied Theme Presets in Settings

**File:** `/workspace/app/services/file_metadata.py`

Add new fields to default settings:
```python
def get_default_settings():
    return {
        # ... existing fields ...
        "applied_video_theme": "",   # NEW: e.g., "night_vision"
        "applied_audio_theme": "",   # NEW: e.g., "vinyl_record"
    }
```

**File:** `/workspace/app/models.py`

Update `UserSettings` model:
```python
class UserSettings(BaseModel):
    # ... existing fields ...
    applied_video_theme: str = ""
    applied_audio_theme: str = ""
```

**File:** `/workspace/app/services/settings.py`

Add function to update applied theme:
```python
def update_applied_theme(
    media_type: str,  # "video" or "audio"
    preset_key: str,  # preset key or "" for none
    filename: str | None = None
) -> UserSettings:
    """Track which theme preset is currently applied."""
```

### Step 2: Update `apply_theme_preset()` Endpoint

**File:** `/workspace/app/routers/audio.py`

Modify to:
1. Store the applied theme key (not just "custom")
2. Clear previous filters for that media type when applying new preset
3. Handle "none" preset key to clear filters

```python
@router.post("/apply-theme-preset/{media_type}/{preset_key}")
async def apply_theme_preset(...):
    if preset_key == "none":
        # Clear custom_values for all filters of this media type
        # Set applied_X_theme = ""
    else:
        # Apply preset filters
        # Set applied_X_theme = preset_key
```

### Step 3: Add "None" Option to Template

**File:** `/workspace/app/templates/partials/filters_presets_accordion.html`

Add a "None" card at the start of each preset section:
```html
<div class="preset-card preset-card--none {% if not applied_video_theme %}preset-card--selected{% endif %}"
     hx-post="/apply-theme-preset/video/none"
     hx-vals="js:{filename: window.currentFilename}">
    <div class="preset-card-icon">
        <i class="fa-solid fa-ban"></i>
    </div>
    <div class="preset-card-content">
        <span class="preset-card-name">None</span>
        <span class="preset-card-description">No theme preset</span>
    </div>
</div>
```

### Step 4: Add Selected State Styling

**File:** `/workspace/app/static/css/filter-chain.css`

Add distinct selected state (different from hover):
```css
.preset-card--selected {
    border-color: var(--accent);
    background: var(--bg-secondary);
    box-shadow: inset 0 0 0 1px var(--accent);
}

.preset-card--selected .preset-card-icon {
    background: var(--accent);
    color: var(--bg-primary);
}

/* Hover still works but doesn't override selected */
.preset-card--selected:hover {
    transform: translateY(-2px);
}
```

### Step 5: Pass Applied Theme to Template Context

**File:** `/workspace/app/routers/audio.py`

Update `_get_accordion_context()` and related functions to include:
```python
context["applied_video_theme"] = user_settings.applied_video_theme
context["applied_audio_theme"] = user_settings.applied_audio_theme
```

Update template to conditionally add `preset-card--selected` class:
```html
<div class="preset-card {% if applied_video_theme == preset_key %}preset-card--selected{% endif %}"
```

### Step 6: Handle Combined Presets

When applying a video preset:
- Only clear/replace video-related filter custom_values
- Preserve any applied audio theme (and vice versa)

Filter categories by media type:
- **Video:** brightness, contrast, saturation, blur, sharpen, transform
- **Audio:** volume, tunnel, frequency, speed, pitch, noise_reduction, compressor

---

## Files to Modify

| File | Changes |
|------|---------|
| `app/models.py` | Add `applied_video_theme`, `applied_audio_theme` to UserSettings |
| `app/services/file_metadata.py` | Add fields to `get_default_settings()` |
| `app/services/settings.py` | Add `update_applied_theme()` function |
| `app/routers/audio.py` | Update `apply_theme_preset()`, add context vars |
| `app/templates/partials/filters_presets_accordion.html` | Add "None" cards, selected class logic |
| `app/static/css/filter-chain.css` | Add `.preset-card--selected` styles |

---

## Verification

1. `task rebuild`
2. Open http://localhost:8000
3. Upload a video file
4. Click "Presets" tab
5. Click "Night Vision" → verify it shows selected state
6. Click "Vinyl Record" (audio) → verify both show selected (video + audio combined)
7. Click "None" under Video → verify Night Vision deselects, Vinyl Record stays
8. Process → verify only audio preset applied
9. Click "None" under Audio → verify Vinyl Record deselects
10. Process → verify no effects applied
