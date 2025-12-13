# CLAUDE.md - FFmpeg Sandbox

## After Every Change

```bash
task rebuild
```

Cleans output/logs/metadata, rebuilds Docker image, restarts container.

## Project Overview

FastAPI + HTMX single-page app for processing audio/video with visual filter chains. 13 filter categories (7 audio, 6 video) with YAML-driven presets.

## Tech Stack

- **Backend**: FastAPI, Pydantic
- **Frontend**: HTMX, Jinja2
- **Processing**: ffmpeg, yt-dlp
- **Config**: PyYAML (config.yml, presets.yml)
- **Package Manager**: uv (Astral)

## Project Structure

```
config.yml               # App configuration
presets.yml              # Filter presets (66 presets, 13 categories)
.data/
├── input/               # Source files + per-file .yml metadata
├── output/              # Processed files
└── logs/                # App logs
app/
├── main.py              # FastAPI entry, index route
├── config.py            # Config loader
├── models.py            # Pydantic schemas (241 lines)
├── routers/
│   ├── audio.py         # /process, /preview, filter chain endpoints
│   ├── download.py      # yt-dlp download endpoints
│   └── history.py       # History endpoints
├── services/
│   ├── __init__.py      # Public API exports
│   ├── presets.py       # YAML preset loader with Pydantic validation
│   ├── processor.py     # FFmpeg processing orchestration
│   ├── metadata.py      # File introspection (duration, codecs)
│   ├── filters_audio.py # Audio filter builders
│   ├── filters_video.py # Video filter builders
│   ├── filter_chain.py  # Filter chain aggregation
│   ├── ffmpeg_executor.py # Subprocess wrapper
│   ├── downloader.py    # yt-dlp downloading
│   ├── file_metadata.py # Per-file YAML metadata
│   ├── history.py       # Processing history
│   └── settings.py      # User settings persistence
├── templates/
│   ├── base.html        # Layout + theme selector
│   ├── index.html       # Main interface
│   └── partials/        # HTMX partials
└── static/css/
    ├── themes.css       # 10 dark themes
    └── styles.css       # Component styles
```

## Key Commands

```bash
uv sync                  # Install deps
uv run python -m app.main  # Dev server
docker compose up -d     # Docker
```

## Filter Categories

**Audio (7):** Volume, Tunnel, Frequency, Speed, Pitch, Noise Reduction, Compressor

**Video (6):** Brightness, Contrast, Saturation, Blur, Sharpen, Transform

All presets defined in `presets.yml`, validated against Pydantic schemas in `models.py`.

## Common Tasks

### Add a new preset

Edit `presets.yml`:

```yaml
audio:
  volume:
    new_preset:
      name: "New Preset"
      description: "Description here"
      volume: 1.5
```

Restart container. Presets are validated on startup via `app/services/presets.py`.

### Add a new theme

Add to `app/static/css/themes.css`:

```css
[data-theme="newtheme"] {
    --bg-primary: #xxx;
    /* ... other vars */
}
```

Add option to `templates/base.html` theme selector.

### Modify filter chain

Edit `app/services/filter_chain.py` for chain logic, or individual `filters_audio.py`/`filters_video.py` for specific filters.

---

## Development Roadmap

### Phase 12: Complete Video Export UI
**Priority:** High | **Status:** 60-70% done

Missing:
- Video player in preview.html (only shows audio)
- Audio vs video export selection
- Format selection (MP4, WebM, MKV)

### Phase 13: Audio Filter QA
**Priority:** Medium | **Status:** Backend ready

- Validate pitch + speed interaction
- Test noise reduction with real audio
- Test extreme speed values (4x)

### Phase 14: Preset Management
**Priority:** Medium-High | **Status:** Not started

- Save custom presets
- Export/import as YAML
- Preset categories (Podcast, Music, etc.)

### Phase 15: Batch Processing
**Priority:** Medium | **Status:** Not started

- Multi-file upload
- Apply chain to all files
- Export as ZIP
- Progress tracking

### Phase 20: Output Format Options
**Priority:** Medium | **Status:** Not started

- Audio: MP3, WAV, FLAC, OGG, AAC
- Video: MP4, WebM, MKV
- Quality/bitrate selection

### Lower Priority
- Phase 16: Waveform/spectrogram visualization
- Phase 17: Performance (caching, large files)
- Phase 18: Mobile responsiveness
- Phase 19: Keyboard shortcuts

---

## Technical Debt (Resolved)

- ~~models.py 771 lines~~ → 241 lines (presets moved to YAML)
- ~~processor.py 669 lines~~ → Split into 6 modules
- ~~Repetitive preset lookups~~ → String-based YAML lookups
