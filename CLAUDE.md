# CLAUDE.md - FFmpeg-sandbox

## Project Overview

A Python-based Single Page Application for extracting and processing audio from video files with tunnel/reverb effects. Built with FastAPI and HTMX for a dynamic, server-rendered experience.

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
config.yml              # Application configuration
app/
├── main.py             # FastAPI entry point, routes index
├── config.py           # Config loader with dataclasses
├── models.py           # Pydantic models, preset definitions
├── routers/
│   ├── audio.py        # /process, /preview, /upload, /clip-preview, /clip-video-preview
│   ├── download.py     # /download/validate, /download/execute
│   └── history.py      # /history endpoints
├── services/
│   ├── processor.py    # ffmpeg audio processing
│   ├── downloader.py   # yt-dlp video downloading
│   └── history.py      # JSON-based history management
├── templates/
│   ├── base.html       # Base layout with theme selector
│   ├── index.html      # Main 3-column interface with ClipRangeController
│   └── partials/       # HTMX partial templates
└── static/
    └── css/
        ├── themes.css  # 10 dark theme definitions
        └── styles.css  # Component styles
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
| GET | `/duration/{filename}` | Get file duration in ms |
| GET | `/clip-preview` | Stream audio clip for range slider |
| GET | `/clip-video-preview` | Stream video clip for modal preview |
| GET | `/partials/sliders?preset=` | Get slider form for preset |
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

### Presets

| Preset | Description | Highpass | Lowpass | Delays |
|--------|-------------|----------|---------|--------|
| none | No effect (default) | 20 Hz | 20000 Hz | none |
| light | Subtle ambience | 80 Hz | 6000 Hz | 10\|20 ms |
| medium | Noticeable reverb | 100 Hz | 4500 Hz | 15\|25\|35\|50 ms |
| heavy | Strong cave effect | 120 Hz | 3500 Hz | 20\|35\|55\|80 ms |
| extreme | Deep bunker sound | 150 Hz | 2500 Hz | 25\|45\|70\|100\|140 ms |

## UI Features

### Clip Range Slider
- Dual-handle slider for precise clip selection (millisecond precision)
- Play/pause/stop controls for audio preview
- Auto-fetches duration when file is selected

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

### Add a new preset

Edit `app/models.py` and add to the `PRESETS` dictionary:

```python
PresetLevel.NEW_PRESET: PresetConfig(
    name="New Preset",
    description="Description here",
    volume=2.0,
    highpass=100,
    lowpass=4000,
    delays=[10, 20, 30],
    decays=[0.3, 0.25, 0.2],
),
```

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
