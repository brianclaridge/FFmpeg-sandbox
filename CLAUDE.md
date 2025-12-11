# CLAUDE.md - FFmpeg-sandbox

## Project Overview

A Python-based Single Page Application for extracting and processing audio from video files with a visual effect chain (Volume → Tunnel → Frequency). Built with FastAPI and HTMX for a dynamic, server-rendered experience.

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: HTMX (hypermedia-driven)
- **Templates**: Jinja2
- **Audio/Video**: ffmpeg, yt-dlp
- **Logging**: loguru
- **Config**: PyYAML
- **Package Manager**: uv (Astral)

## Project Structure

```
config.yml               # Application configuration
.data/
├── input/               # Source video/audio files
├── output/              # Processed audio files
├── user_settings.yml    # Persistent user preferences
└── history.json         # Processing history
app/
├── main.py              # FastAPI entry point, routes index
├── config.py            # Config loader with dataclasses
├── models.py            # Pydantic models, category presets, enums
├── routers/
│   ├── audio.py         # /process, /preview, /upload, effect chain endpoints
│   ├── download.py      # /download/validate, /download/execute
│   └── history.py       # /history endpoints
├── services/
│   ├── processor.py     # ffmpeg audio processing + file metadata
│   ├── downloader.py    # yt-dlp video downloading
│   ├── history.py       # JSON-based history management
│   └── settings.py      # User settings YAML persistence
├── templates/
│   ├── base.html        # Base layout with theme selector
│   ├── index.html       # Main 3-column interface with ClipRangeController
│   └── partials/
│       ├── effect_chain.html       # Effect chain container
│       ├── effect_chain_boxes.html # Clickable Volume/Tunnel/Frequency boxes
│       ├── panel_volume.html       # Volume category controls
│       ├── panel_tunnel.html       # Tunnel/echo category controls
│       └── panel_frequency.html    # Frequency/EQ category controls
└── static/
    └── css/
        ├── themes.css   # 10 dark theme definitions
        └── styles.css   # Component styles
```

## Key Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python -m app.main

# Or use the entry point
uv run audio-processor

# Docker
docker compose up -d
```

## Configuration

All settings are externalized to `config.yml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  version: "0.1.0"
  reload: true

logging:
  rotation: "10 MB"
  retention: "7 days"
  stderr_level: "INFO"
  file_level: "DEBUG"

history:
  max_entries: 50

download:
  filename_max_length: 50
  format: "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

audio:
  allowed_extensions: [".mp4", ".mkv", ".avi", ".mov", ".webm", ".mp3", ".wav", ".flac", ".m4a", ".ogg"]
  preview_timeout: 30
  mp3_quality: "4"
  default_preset: "none"
  default_start_time: "00:00:00"
  default_end_time: "00:00:06"
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page |
| POST | `/process` | Process audio, returns preview partial |
| POST | `/upload` | Upload file to input directory |
| GET | `/preview/{filename}` | Serve processed audio file |
| GET | `/duration/{filename}` | Get file metadata (duration, codecs, resolution) |
| GET | `/clip-preview` | Stream audio clip for range slider |
| GET | `/clip-video-preview` | Stream video clip for modal preview |
| GET | `/partials/effect-chain` | Get effect chain UI component |
| GET | `/partials/category-panel/{cat}` | Get category control panel |
| POST | `/partials/category-preset/{cat}/{preset}` | Set category preset |
| POST | `/download/validate` | Validate URL via yt-dlp |
| POST | `/download/execute` | Download from URL |
| GET | `/history` | Get history partial |
| DELETE | `/history/{id}` | Delete history entry |
| GET | `/history/{id}/apply` | Apply history settings to form |

## Audio Processing

The processor uses ffmpeg with this filter chain:

```
volume={vol},highpass=f={hp},lowpass=f={lp},aecho=0.8:0.85:{delays}:{decays}
```

### Effect Chain Categories

The UI organizes processing into three independent categories:

**Volume** (`VolumePreset`): 1x, 1.5x, 2x, 3x, 4x

**Tunnel** (`TunnelPreset`): None, Subtle, Medium, Heavy, Extreme

**Frequency** (`FrequencyPreset`): Flat, Bass Cut, Treble Cut, Narrow Band, Voice Clarity

Each category has its own presets and controls. User selections persist to `.data/user_settings.yml`.

## UI Features

### Visual Effect Chain
- Three clickable boxes: Volume → Tunnel → Frequency
- Clicking a box reveals its category control panel
- Per-category preset pills for quick selection
- Active category highlighted in the chain
- Settings persist to `.data/user_settings.yml`

### File Metadata Display
- Shows after file selection below the Process button
- Displays: filename, duration, file size
- For video: resolution, frame rate, video codec
- For all: audio codec, sample rate, channels, bitrate

### Clip Range Slider
- Dual-handle slider for precise clip selection (millisecond precision)
- **Defaults to full file duration** (0 to end)
- Play/pause/stop controls for audio preview
- Auto-fetches duration and metadata when file is selected

### Video Preview Modal
- Draggable modal window (defaults to bottom-right)
- Appears only for video files
- Loops the selected clip range
- Follows current theme

### Themes

10 dark themes defined in `static/css/themes.css`:
- Darcula (default), Dracula, Monokai, Nord, Solarized
- Gruvbox, One Dark, Tokyo Night, Catppuccin, Neon

Theme selection via `data-theme` attribute, persisted in localStorage.

## Development Notes

- Source files: `.data/input/` (or upload/URL download)
- Output files: `.data/output/`
- History: `.data/history.json` (max configurable)
- Logs: `.data/logs/app.log` (retention configurable)

## Common Tasks

### Add a new category preset

Each category has its own enum and preset dictionary in `app/models.py`:

```python
# Add to enum
class TunnelPreset(str, Enum):
    # ... existing ...
    NEW_PRESET = "new_preset"

# Add to dictionary
TUNNEL_PRESETS[TunnelPreset.NEW_PRESET] = TunnelConfig(
    name="New Preset",
    description="Description here",
    delays=[10, 20, 30],
    decays=[0.3, 0.25, 0.2],
)
```

Don't forget to also add to the `*_BY_STR` dictionary if accessing via string keys in templates.

### Add a new theme

Add to `app/static/css/themes.css`:

```css
[data-theme="newtheme"] {
    --bg-primary: #xxx;
    --bg-secondary: #xxx;
    --bg-card: #xxx;
    --bg-input: #xxx;
    --text-primary: #xxx;
    --text-secondary: #xxx;
    --accent: #xxx;
    --accent-hover: #xxx;
    --success: #xxx;
    --error: #xxx;
    --slider-track: #xxx;
    --slider-border: #xxx;
}
```

Then add option to `templates/base.html` theme selector.

### Modify the filter chain

Edit `app/services/processor.py` in the `process_audio` function.

### Add new form fields

1. Add field to `ProcessRequest` in `models.py`
2. Add HTML input in `templates/index.html`
3. Add handling in `routers/audio.py`

### Update configuration

Edit `config.yml` and restart the application. All settings are loaded at startup via `app/config.py`.
