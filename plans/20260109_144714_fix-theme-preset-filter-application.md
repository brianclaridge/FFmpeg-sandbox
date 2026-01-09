# Plan: Fix Theme Preset Filter Application

**Affects:** `/workspace/app/routers/audio.py`, `/workspace/app/services/settings.py`

---

## Problem

Theme presets (Night Vision, VHS, Vinyl, etc.) display correctly but clicking them does not apply any filters. The "Process" button produces output with no effects applied.

## Root Cause

1. **audio.py:1040** - `apply_theme_preset()` endpoint sets all filters to `"none"` instead of applying actual parameters (incomplete TODO)
2. **audio.py:109-123** - `/process` endpoint ignores `custom_values` field in UserSettings

## Fix

### Step 1: Add `update_category_custom_values()` to settings.py

**File:** `/workspace/app/services/settings.py`

Add new function to store custom filter values:

```python
def update_category_custom_values(
    category: str,
    custom_values: dict,
    filename: str | None = None
) -> None:
    """Update custom values for a filter category."""
    settings = load_user_settings(filename)
    if hasattr(settings, category):
        cat_settings = getattr(settings, category)
        cat_settings.preset = "custom"  # Mark as custom
        cat_settings.custom_values = custom_values
        _save_settings(settings, filename)
```

### Step 2: Fix `apply_theme_preset()` endpoint

**File:** `/workspace/app/routers/audio.py` (lines 1018-1049)

Replace the broken implementation:

```python
# OLD (broken):
update_category_preset(filter_type, "none", filename)

# NEW (working):
from app.services.settings import update_category_custom_values
update_category_custom_values(filter_type, filter_step.params, filename)
```

### Step 3: Update `/process` to use custom_values

**File:** `/workspace/app/routers/audio.py` (lines 109-123)

For each filter category, check `custom_values` first:

```python
# Example for saturation:
if user_settings.saturation.custom_values:
    saturation_value = user_settings.saturation.custom_values.get("saturation", 1.0)
else:
    saturation_config = saturation_presets.get(user_settings.saturation.preset) or saturation_presets["none"]
    saturation_value = saturation_config.saturation
```

Apply this pattern to all 13 filter categories.

---

## Files to Modify

1. `/workspace/app/services/settings.py` - Add `update_category_custom_values()` function
2. `/workspace/app/routers/audio.py` - Fix `apply_theme_preset()` and `/process` endpoint

---

## Verification

1. Run `task rebuild`
2. Open http://localhost:8000
3. Upload/select a video file
4. Click "Presets" tab
5. Click "Night Vision" preset
6. Click "Process" button
7. Verify output video has: reduced saturation (0.3), increased brightness (+0.2), increased contrast (1.4)
8. Test audio preset "Vinyl Record" with an audio file
