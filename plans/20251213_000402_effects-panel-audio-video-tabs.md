# Plan: Effects Panel with Audio/Video Tabs

## Overview
Rename "Effect Chain" to "Effects" and implement a tabbed interface separating Audio and Video effects. Expand output capabilities to include video export with applied effects.

## User Requirements (Confirmed)
- **Audio Effects**: Speed, Pitch, Noise Reduction, Compressor (ALL selected)
- **Video Effects**: Speed, Color Grading, Blur/Sharpen, Transform (ALL selected)
- **Speed Sync**: Linked (single control affects both audio and video)
- **Output**: Expand to video export (MP4 with effects applied)

---

## Implementation Phases

### Phase 1: Foundation - Tab Infrastructure
**Files:**
- `app/templates/index.html` - Rename "Effect Chain" to "Effects"
- `app/templates/partials/effects_tabs.html` (NEW) - Tab container with [Audio] [Video] buttons
- `app/static/css/effect-chain.css` - Add tab styles
- `app/models.py` - Add `active_tab: str = "audio"` to UserSettings

### Phase 2: New Audio Effects
**Add to `app/models.py`:**

| Effect | Enum | FFmpeg Filter | Presets |
|--------|------|---------------|---------|
| Speed | `SpeedPreset` | `atempo` | 0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x |
| Pitch | `PitchPreset` | `asetrate+atempo` | Low, Normal, High, Chipmunk |
| Noise Reduction | `NoiseReductionPreset` | `afftdn` | Off, Light, Medium, Heavy |
| Compressor | `CompressorPreset` | `acompressor` | Off, Light, Podcast, Broadcast |

**Files:**
- `app/templates/partials/effects_audio_accordion.html` (rename existing)
- `app/services/processor.py` - Add filter builders

### Phase 3: Video Effects
**Add to `app/models.py`:**

| Effect | Enum | FFmpeg Filter | Presets |
|--------|------|---------------|---------|
| Brightness | `BrightnessPreset` | `eq` | Dark, Normal, Bright |
| Contrast | `ContrastPreset` | `eq` | Low, Normal, High |
| Saturation | `SaturationPreset` | `eq` | Grayscale, Muted, Normal, Vivid |
| Blur | `BlurPreset` | `gblur` | None, Light, Medium, Heavy |
| Sharpen | `SharpenPreset` | `unsharp` | None, Light, Medium, Strong |
| Transform | `TransformPreset` | `hflip/vflip/transpose` | None, Flip H, Flip V, 90°, 180°, 270° |

**Files:**
- `app/templates/partials/effects_video_accordion.html` (NEW)
- `app/services/processor.py` - Add `build_video_filter_chain()`

### Phase 4: Speed Synchronization
- Single Speed control in Audio tab
- Audio: `atempo=X` filter
- Video: `setpts=(1/X)*PTS` filter
- Both applied together for A/V sync

### Phase 5: Video Export
**Files:**
- `app/services/processor.py` - Add `process_video_with_effects()`
- `app/routers/audio.py` - Add `/export-video` endpoint
- `app/templates/partials/video_preview.html` (NEW)
- `app/templates/index.html` - Add "Export Video" button

---

## Critical Files

| File | Changes |
|------|---------|
| `app/models.py` | +11 effect enums, +11 config classes, +11 preset dictionaries |
| `app/services/processor.py` | +filter builders, +`process_video_with_effects()` |
| `app/routers/audio.py` | +tab endpoints, +`/export-video` |
| `app/templates/partials/effects_tabs.html` | NEW - Tab container |
| `app/templates/partials/effects_audio_accordion.html` | Renamed, +4 new sections |
| `app/templates/partials/effects_video_accordion.html` | NEW - 6 video sections |
| `app/templates/partials/video_preview.html` | NEW - Video output player |
| `app/static/css/effect-chain.css` | +Tab styles |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/partials/effects-tab/{tab}` | Get tab content (audio/video) |
| POST | `/partials/effects-preset/{category}/{preset}` | Set effect preset |
| POST | `/export-video` | Export video with effects |

---

## Edge Cases
1. **Audio-only files + Export Video**: Hide button or show error
2. **Extreme speed**: Chain multiple atempo filters (0.5-2.0 range each)
3. **Pitch + Speed**: Apply pitch correction before speed filter
4. **Settings migration**: Existing YAML files get defaults for new keys

---

## TODO

### Phase 1: Foundation ✅ COMPLETE
- [x] Rename "Effect Chain" heading to "Effects"
- [x] Create effects_tabs.html template
- [x] Add tab CSS styles (.effects-tabs, .effects-tab-bar, .effects-tab)
- [x] Update UserSettings with active_tab field
- [x] Add /partials/effects-tab/{tab} endpoint

### Phase 2: Audio Effects ✅ COMPLETE (UI)
- [x] Add SpeedPreset enum, SpeedConfig, SPEED_PRESETS
- [x] Add PitchPreset enum, PitchConfig, PITCH_PRESETS
- [x] Add NoiseReductionPreset enum, config, presets
- [x] Add CompressorPreset enum, config, presets
- [x] Rename effect_chain_accordion.html to effects_audio_accordion.html
- [x] Add accordion sections for new audio effects
- [ ] Implement build_atempo_filter() in processor.py
- [ ] Implement build_pitch_filter() in processor.py
- [ ] Implement build_noise_reduction_filter() in processor.py
- [ ] Implement build_compressor_filter() in processor.py

### Phase 3: Video Effects ✅ COMPLETE (UI)
- [x] Add BrightnessPreset, ContrastPreset, SaturationPreset
- [x] Add BlurPreset, SharpenPreset, TransformPreset
- [x] Create effects_video_accordion.html template
- [ ] Implement build_video_filter_chain() in processor.py

### Phase 4: Speed Sync
- [ ] Implement linked speed control (audio atempo + video setpts)

### Phase 5: Video Export
- [ ] Add process_video_with_effects() function
- [ ] Add /export-video endpoint
- [ ] Create video_preview.html template
- [ ] Add "Export Video" button to UI
- [ ] Update per-file settings persistence for new effects

### Testing
- [ ] Test all effect combinations
- [ ] Test with various file formats (mp4, mkv, webm)
- [ ] Test audio-only file handling
