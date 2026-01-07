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
Root Files:
├── config.yml           # App configuration
├── presets.yml          # Filter shortcuts (66 shortcuts, 13 categories)
├── presets_themes.yml   # Theme presets (12 presets: 6 video, 6 audio)
├── Dockerfile           # Container build
├── docker-compose.yml   # Container orchestration
├── docker-entrypoint.sh # Container startup script
├── Taskfile.yml         # Task runner commands
├── pyproject.toml       # Python dependencies (uv)
└── scripts/             # Development utilities
    ├── debug-path.ps1
    ├── diagnose-logs.ps1
    ├── docker-compose-wrapper.ps1
    ├── health-check.ps1
    ├── setup-dirs.ps1
    └── test-ytdlp.ps1

.data/
├── input/               # Source files + per-file .yml metadata
├── output/              # Processed files
└── logs/                # App logs

app/
├── main.py              # FastAPI entry, index route
├── config.py            # Config loader
├── models.py            # Pydantic schemas (240 lines)
├── routers/
│   ├── audio.py         # /process, /preview, filter chain endpoints
│   ├── download.py      # yt-dlp download endpoints
│   └── history.py       # History endpoints
├── services/
│   ├── __init__.py      # Public API exports
│   ├── presets.py       # YAML shortcut loader with Pydantic validation
│   ├── presets_themes.py # Theme preset loader (VHS, Vinyl, etc.)
│   ├── user_shortcuts.py # User shortcut CRUD operations
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
│   └── partials/
│       ├── download_complete.html   # Download success message
│       ├── download_status.html     # Download progress
│       ├── filters_audio_accordion.html  # Audio filter UI (shortcuts)
│       ├── filters_presets_accordion.html # Theme presets UI
│       ├── filters_tabs.html        # Audio/Video/Presets tab switcher
│       ├── filters_video_accordion.html  # Video filter UI (shortcuts)
│       ├── history.html             # Processing history list
│       ├── history_preview.html     # History item preview
│       ├── preview.html             # Audio/video preview player
│       ├── slider_form.html         # Clip range slider
│       └── upload_status.html       # File upload feedback
└── static/css/
    ├── base.css         # CSS reset, variables
    ├── buttons.css      # Button components
    ├── components.css   # Reusable UI components
    ├── filter-chain.css # Filter chain styling
    ├── forms.css        # Form elements
    ├── layout.css       # Page layout, grid
    ├── media.css        # Audio/video player styles
    ├── modal.css        # Modal dialogs
    ├── styles.css       # Main stylesheet (imports)
    └── themes.css       # 10 dark themes
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

### Phase 13: Audio Filter QA
**Priority:** Medium | **Status:** Backend ready

- Validate pitch + speed interaction
- Test noise reduction with real audio
- Test extreme speed values (4x)

### Phase 14: Shortcut Management
**Priority:** Medium-High | **Status:** Complete

- Save custom shortcuts (filter presets)
- Export/import as YAML
- Shortcut categories (Podcast, Music, Custom)

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

### Phase 21: Presets Tab + Terminology Refactor
**Priority:** High | **Status:** Complete

- Renamed filter presets to "Shortcuts" (quick slider values)
- Added 3rd "Presets" tab for themed transformation pipelines
- Video presets: VHS Playback, Film Grain, Silent Film, Security Cam, Glitch Art, Night Vision
- Audio presets: Vinyl Record, Old Radio, Telephone, Cassette Tape, Podcast Ready, Underwater
- YAML-driven preset definitions (`presets_themes.yml`)
- New service: `presets_themes.py` for theme preset management

### Lower Priority
- Phase 16: Waveform/spectrogram visualization
- Phase 17: Performance (caching, large files)
- Phase 18: Mobile responsiveness
- Phase 19: Keyboard shortcuts

---

## Technical Debt (Resolved)

- ~~models.py 771 lines~~ → 240 lines (presets moved to YAML)
- ~~processor.py 669 lines~~ → Split into 6 modules
- ~~Repetitive preset lookups~~ → String-based YAML lookups
