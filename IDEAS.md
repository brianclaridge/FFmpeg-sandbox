# FFmpeg Sandbox - Development Ideas

## Current Status

**Project Completion:** ~70% feature-complete

**Implemented (Phases 1-11):**
- Audio/Video effects UI (tabs, accordions)
- 13 effect categories with preset definitions
- FFmpeg filter builders for all effects
- Per-file YAML metadata persistence
- Video preview modal with clip range
- Effect chain accordion UI
- Hidden form inputs for all presets

**Codebase Stats:**
- ~2,400 lines Python
- Well-structured: models/services/routers separation
- 60+ preset variations across 13 effects

---

## Development Phases

### Phase 12: Complete Video Export UI
**Priority:** High | **Status:** 60-70% done

**What's Done:**
- `build_video_filter_chain()` fully implemented
- `process_video_with_effects()` called from `/process`
- Video tab UI skeleton exists

**What's Missing:**
1. Video player in `preview.html` (only shows audio player for `.mp3`)
2. Explicit audio vs video export selection in form
3. Format selection dropdown (MP4, WebM, MKV)

**Files:**
- `app/templates/partials/preview.html`
- `app/routers/audio.py`

---

### Phase 13: Audio Effect Testing/Tuning
**Priority:** Medium | **Status:** Backend ready, needs QA

**Tasks:**
1. Validate pitch + speed interaction (order of operations)
2. Test noise reduction presets with real audio
3. Verify compressor "Podcast" and "Broadcast" presets
4. Test extreme speed values (4x) for artifacts
5. Consider `rubberband` library for higher-quality pitch shifting

**Files:**
- `app/services/processor.py`
- `app/models.py` (preset values)

---

### Phase 14: Preset Management
**Priority:** Medium-High | **Status:** Not started

**Features:**
1. Save custom presets (user-defined effect combinations)
2. Export/import presets as YAML
3. Preset categories: Podcast, Music, Tutorial, Gaming
4. Recent presets / favorites quick access

**Implementation:**
- Add `custom_presets` array to `UserSettings` model
- Create `/api/presets/save` and `/api/presets/list` endpoints
- Preset management UI (list, delete, reorder)

---

### Phase 15: Batch Processing
**Priority:** Medium | **Status:** Not started

**Features:**
1. Upload multiple files with drag-and-drop
2. Apply same effect chain to all selected files
3. Export all as ZIP
4. Progress bar for batch operations
5. Queue with status tracking

**Architecture Considerations:**
- Task queue (Celery/RQ) for async processing
- Status endpoint: `/job/{job_id}`
- Background worker container

---

### Phase 16: Effect Chain Visualization
**Priority:** Lower | **Status:** Not started

**Features:**
1. Real-time waveform preview with effects applied
2. Flowchart visualization: Input → Effects → Output
3. A/B comparison mode (Original vs Processed side-by-side)
4. Spectrogram view for frequency effects

---

### Phase 17: Performance & Scalability
**Priority:** Lower | **Status:** Not started

**Issues to Address:**
1. Preview caching (currently regenerates each time)
2. Large file handling (30+ second processing blocks UI)
3. Output storage cleanup (no retention policy)
4. Concurrent processing limits

**Solutions:**
- Cache previews per timestamp range
- Show long-running task status indicator
- Add retention policy (14 days) + manual cleanup
- Request queuing for concurrent users

---

### Phase 18: Mobile Responsiveness
**Priority:** Lowest | **Status:** Not started

**Issues:**
- 4-column grid breaks on phones
- Range sliders hard to use on touch
- Effect accordion stacks poorly

**Quick Wins:**
- CSS media query: stack columns on <768px
- Touch-friendly button sizes (44px minimum)
- Vertical range slider for mobile

---

### Phase 19: Keyboard Shortcuts
**Priority:** Low | **Status:** Not started

**Ideas:**
- `Alt+A` / `Alt+V` - Switch audio/video tabs
- `1-9` - Quick preset selection
- `Space` - Play/pause preview
- `P` - Process current file
- `Esc` - Close modal

---

### Phase 20: Output Format Options
**Priority:** Medium | **Status:** Not started

**Audio Formats:**
- MP3 (current default)
- WAV (lossless)
- FLAC (lossless compressed)
- OGG (open format)
- AAC/M4A

**Video Formats:**
- MP4 (H.264)
- WebM (VP9)
- MKV (container)

**Quality Options:**
- Bitrate selection
- Sample rate selection
- Codec presets (fast/balanced/quality)

---

## Technical Debt

### Code Organization
- `app/models.py`: 771 lines - extract video effects to separate module
- `app/routers/audio.py`: 734 lines - split into audio/video routers
- Repetitive preset lookup code - use factory pattern

### Missing Infrastructure
- No test suite (add pytest for filter validation)
- No type hints in template context dictionaries
- Settings loading has no caching (loads YAML per request)

### Known Bugs
1. ~~Preset persistence bug~~ (fixed in Phase 7-10)
2. ~~Volume "1x" vs "None" conflict~~ (fixed in Phase 11)

---

## Code Quality Observations

**Strengths:**
- Clear model/service/router separation
- Comprehensive preset system
- Per-file YAML metadata for settings persistence
- Well-documented filter builder functions
- HTMX-driven SPA with minimal JavaScript

**Areas for Improvement:**
- Add pytest test coverage
- Extract large files into modules
- Add request caching for settings
- Consider TypeScript for complex JS logic

---

## Suggested Roadmap

| Priority | Phase | Focus |
|----------|-------|-------|
| Next | 12 | Complete Video Export UI |
| Soon | 14 | Preset Management |
| Medium | 13 | Audio Effect QA/Tuning |
| Medium | 20 | Output Format Options |
| Later | 15 | Batch Processing |
| Later | 16-19 | Polish & Features |
