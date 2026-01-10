# Plan: Enhance Video Theme Presets

**Affects:** `/workspace/presets_themes.yml`, `/workspace/app/services/filters_video.py`, `/workspace/app/services/filter_chain.py`, `/workspace/app/models.py`, `/workspace/app/services/presets.py`

---

## Requirements

1. **VHS Playback**: Crop to 4:3 aspect ratio (cut sides)
2. **Glitch Art**: More noticeable color shifts and artifacts
3. **Security Cam**: Add text overlays (timestamp, "REC" indicator, camera ID)

---

## Implementation

### Step 1: Add Crop Filter for Aspect Ratio

**File:** `/workspace/app/services/filters_video.py`

```python
def build_crop_filter(aspect_ratio: str) -> str:
    """
    Build crop filter for aspect ratio change.

    Supported ratios: "4:3", "16:9", "1:1"
    Crops from center, removing sides.
    """
    if not aspect_ratio or aspect_ratio == "original":
        return ""

    # Map aspect ratio to crop expression
    # crop=out_w:out_h:x:y - crop to center
    ratios = {
        "4:3": "crop=ih*4/3:ih",      # Crop width to 4:3
        "16:9": "crop=ih*16/9:ih",    # Crop width to 16:9
        "1:1": "crop=min(iw\\,ih):min(iw\\,ih)",  # Square crop
    }
    return ratios.get(aspect_ratio, "")
```

### Step 2: Add Drawtext Filter for Overlays

**File:** `/workspace/app/services/filters_video.py`

```python
def build_overlay_filter(overlay_type: str) -> str:
    """
    Build drawtext filter for video overlays.

    Types: "security_cam", "timestamp", etc.
    """
    if overlay_type == "security_cam":
        # Timestamp top-left, REC indicator top-right, CAM ID bottom-left
        return (
            "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
            "text='%{localtime\\:%Y-%m-%d %H\\\\:%M\\\\:%S}':"
            "fontcolor=white:fontsize=18:x=10:y=10,"
            "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
            "text='● REC':fontcolor=red:fontsize=18:x=w-tw-10:y=10,"
            "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
            "text='CAM 01':fontcolor=white:fontsize=16:x=10:y=h-th-10"
        )
    return ""
```

### Step 3: Add Color Shift Filter for Glitch Effect

**File:** `/workspace/app/services/filters_video.py`

```python
def build_colorshift_filter(shift_amount: int) -> str:
    """
    Build rgbashift filter for glitch-like color channel displacement.

    shift_amount: pixel displacement for red/blue channels
    """
    if shift_amount <= 0:
        return ""

    # Shift red left, blue right for classic glitch look
    return f"rgbashift=rh=-{shift_amount}:bh={shift_amount}"
```

### Step 4: Update Filter Chain

**File:** `/workspace/app/services/filter_chain.py`

Add new parameters to `build_video_filter_chain()`:
- `crop_aspect: str = ""`
- `overlay: str = ""`
- `colorshift: int = 0`

Apply crop first (before other filters), overlay last (after all effects).

### Step 5: Add New Filter Types to Models

**File:** `/workspace/app/models.py`

Add new config classes:
```python
class CropConfig(BaseModel):
    aspect_ratio: str = "original"

class OverlayConfig(BaseModel):
    overlay_type: str = ""

class ColorshiftConfig(BaseModel):
    shift_amount: int = 0
```

### Step 6: Update Theme Presets

**File:** `/workspace/presets_themes.yml`

```yaml
video:
  vhs_playback:
    name: "VHS Playback"
    description: "4:3 retro VHS look with color distortion"
    icon: "fa-vhs"
    filters:
      - type: crop
        params:
          aspect_ratio: "4:3"
      - type: saturation
        params:
          saturation: 1.3
      - type: contrast
        params:
          contrast: 1.2
      - type: blur
        params:
          sigma: 0.5

  glitch_art:
    name: "Glitch Art"
    description: "Digital artifacts and color shifts"
    icon: "fa-bug"
    filters:
      - type: colorshift
        params:
          shift_amount: 5
      - type: saturation
        params:
          saturation: 1.8
      - type: sharpen
        params:
          amount: 3.0
      - type: contrast
        params:
          contrast: 1.5

  security_cam:
    name: "Security Cam"
    description: "Low-fi surveillance with timestamp overlay"
    icon: "fa-video"
    filters:
      - type: saturation
        params:
          saturation: 0.0
      - type: contrast
        params:
          contrast: 1.5
      - type: blur
        params:
          sigma: 0.3
      - type: overlay
        params:
          overlay_type: "security_cam"
```

### Step 7: Wire New Filters to Processing

**File:** `/workspace/app/routers/audio.py`

Update processor call to include new filter values:
- Extract crop/overlay/colorshift from custom_values
- Pass to `build_video_filter_chain()`

---

## Files to Modify

| File | Changes |
|------|---------|
| `Dockerfile` | Add fonts-dejavu-core package for drawtext |
| `app/services/filters_video.py` | Add crop, overlay, colorshift filter functions |
| `app/services/filter_chain.py` | Add new parameters, apply filters in correct order |
| `app/models.py` | Add CropConfig, OverlayConfig, ColorshiftConfig |
| `app/services/presets.py` | Register new config types |
| `app/services/file_metadata.py` | Add default settings for new categories |
| `app/routers/audio.py` | Wire new filter values to processor |
| `presets_themes.yml` | Update VHS, Glitch Art, Security Cam presets |

---

## Font Dependency

Security cam overlay requires a monospace font.

**File:** `/workspace/Dockerfile`

Update apt-get install to include fonts:
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl fonts-dejavu-core && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

Font path for drawtext: `/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf`

---

## Verification

1. `task rebuild`
2. Open http://localhost:8000
3. Upload a 16:9 video file
4. Apply "VHS Playback" → Verify video is cropped to 4:3
5. Apply "Glitch Art" → Verify visible color displacement/artifacts
6. Apply "Security Cam" → Verify timestamp, REC indicator, CAM ID overlays appear
7. Process and download → Verify effects in output file
