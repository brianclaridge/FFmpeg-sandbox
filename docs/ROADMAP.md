# Development Roadmap

Feature development priorities for FFmpeg Sandbox.

---

## High Priority

### Output Format Options
**Status:** Not started

- Audio formats: MP3, WAV, FLAC, OGG, AAC
- Video formats: MP4, WebM, MKV
- Quality/bitrate selection UI
- Codec selection (H.264, H.265, VP9)

### Batch Processing
**Status:** Not started

- Multi-file upload interface
- Apply filter chain to all files
- Export as ZIP archive
- Concurrent processing with queue
- Progress tracking per file

---

## Medium Priority

### Audio Filter QA
**Status:** Backend ready

- Validate pitch + speed interaction
- Test noise reduction with real audio
- Test extreme speed values (4x)
- Document filter interaction matrix

### Waveform Visualization
**Status:** Not started

- Audio waveform display
- Spectrogram view toggle
- Visual clip range selection on waveform
- Real-time preview marker

### Preset Sharing
**Status:** Not started

- Export themed presets as YAML
- Import presets from file
- Preset versioning
- Shareable preset URLs

---

## Lower Priority

### Performance Optimization
**Status:** Not started

- FFmpeg command caching
- Large file chunked processing
- Background job queue (Celery/RQ)
- CDN for processed files

### Mobile Responsive UI
**Status:** Not started

- Touch-friendly sliders
- Responsive layout breakpoints
- Mobile-optimized preview player
- Swipe gestures for tabs

### Keyboard Shortcuts
**Status:** Not started

- Spacebar: Play/pause preview
- Arrow keys: Adjust clip range
- Ctrl+P: Process
- Tab: Switch filter tabs

---

## Future Ideas

| Feature | Description |
|---------|-------------|
| **Real-time Preview** | Live filter preview without processing |
| **Audio Normalization** | LUFS-based loudness normalization |
| **Video Stabilization** | FFmpeg deshake/vidstab filter |
| **Subtitle Overlay** | SRT/VTT subtitle burn-in |
| **Custom FFmpeg Builder** | Advanced mode with raw FFmpeg command |
| **Preset Marketplace** | Community preset sharing |
| **API Mode** | REST API for programmatic access |
| **WebSocket Progress** | Real-time progress via WebSocket |
| **Undo/Redo** | Filter change history with rollback |
| **A/B Comparison** | Side-by-side before/after preview |
| **GPU Acceleration** | NVENC/VAAPI hardware encoding |
| **Cloud Storage** | S3/GCS input/output integration |
| **Scheduled Processing** | Cron-based batch jobs |
| **Watermark Overlay** | Image/text watermark support |
| **GIF Export** | Animated GIF output format |
| **Thumbnail Generation** | Video thumbnail extraction |
| **Audio Extraction** | Extract audio track from video |
| **Video Concatenation** | Join multiple clips |
| **Fade In/Out** | Audio/video fade transitions |
| **Silence Detection** | Auto-trim silent sections |

---

## Completed Phases

<details>
<summary>Shortcut Management</summary>

- Save custom shortcuts (filter presets)
- Export/import as YAML
- Shortcut categories (Podcast, Music, Custom)

</details>

<details>
<summary>Presets Tab + Terminology Refactor</summary>

- Renamed filter presets to "Shortcuts" (quick slider values)
- Added 3rd "Presets" tab for themed transformation pipelines
- Video presets: VHS Playback, Film Grain, Silent Film, Security Cam, Glitch Art, Night Vision, CRT Playback
- Audio presets: Vinyl Record, Old Radio, Telephone, Cassette Tape, Podcast Ready, Underwater
- YAML-driven preset definitions (`presets_themes.yml`)
- New service: `presets_themes.py` for theme preset management

</details>

<details>
<summary>Processing Progress Modal</summary>

- SSE-based progress streaming
- Modal with progress bar during processing
- Cancel button support
- Automatic history refresh on complete

</details>

<details>
<summary>History Apply + Video Preview</summary>

- Apply button restores all 13 filter presets
- Video files render with video player (not audio)
- Fixed template path and context

</details>

---

## Technical Debt (Resolved)

| Issue | Resolution |
|-------|------------|
| models.py 771 lines | Reduced to 240 lines (presets moved to YAML) |
| processor.py 669 lines | Split into 6 focused modules |
| Repetitive preset lookups | String-based YAML lookups |
