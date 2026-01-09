# Plan: Fix Blank Presets Tab Panels

**Affects:** `/workspace/app/main.py`, `/workspace/app/services/presets_themes.py`

---

## Problem

The Presets tab (3rd tab with themed transformations like VHS, Vinyl, etc.) displays blank panels for both audio and video sections.

## Root Cause

Three interconnected issues:

1. **Relative path in service** - `presets_themes.py:17` uses `"presets_themes.yml"` which fails when working directory differs from project root (Docker)

2. **No startup initialization** - `main.py:81` calls `load_presets()` but not `load_theme_presets()`, so theme presets are never loaded

3. **Missing template context** - `main.py:187-229` index() function does not include `video_theme_presets` or `audio_theme_presets` in the template context

---

## Fix

### Step 1: Fix path in presets_themes.py

**File:** `/workspace/app/services/presets_themes.py`

Change line 17 from:
```python
def load_theme_presets(presets_file: Path | str = "presets_themes.yml") -> dict[str, dict[str, ThemePreset]]:
```

To:
```python
def load_theme_presets(presets_file: Path | str | None = None) -> dict[str, dict[str, ThemePreset]]:
```

Add path resolution at start of function (after line 26):
```python
if presets_file is None:
    from app.config import BASE_DIR
    presets_file = BASE_DIR / "presets_themes.yml"
```

### Step 2: Add startup initialization in main.py

**File:** `/workspace/app/main.py`

After line 81 (`load_presets()`), add:
```python
from app.services.presets_themes import load_theme_presets
load_theme_presets()
```

### Step 3: Add theme presets to index() context

**File:** `/workspace/app/main.py`

In the index() function, before the return statement (~line 187):

Add imports/calls:
```python
from app.services.presets_themes import get_video_theme_presets, get_audio_theme_presets
video_theme_presets = get_video_theme_presets()
audio_theme_presets = get_audio_theme_presets()
```

Add to template context dict (after line 224):
```python
# Theme presets for Presets tab
"video_theme_presets": video_theme_presets,
"audio_theme_presets": audio_theme_presets,
```

---

## Verification

1. Run `task rebuild` to rebuild and restart container
2. Open browser to http://localhost:8000
3. Click "Presets" tab (3rd tab)
4. Verify Video section shows: VHS Playback, Film Grain, Silent Film, Security Cam, Glitch Art, Night Vision
5. Verify Audio section shows: Vinyl Record, Old Radio, Telephone, Cassette Tape, Podcast Ready, Underwater
6. Refresh page - panels should still be populated
