# CLAUDE.md - FFmpeg-sandbox

## Project Overview

A Python-based Single Page Application for extracting and processing audio from video files with tunnel/reverb effects. Built with FastAPI and HTMX for a dynamic, server-rendered experience.

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: HTMX (hypermedia-driven)
- **Templates**: Jinja2
- **Audio**: ffmpeg, yt-dlp
- **Logging**: loguru
- **Package Manager**: uv (Astral)

## Project Structure

```
app/
├── main.py             # FastAPI entry point, routes index
├── config.py           # Path configuration
├── models.py           # Pydantic models, preset definitions
├── routers/
│   ├── audio.py        # /process, /preview, /upload, /partials/sliders
│   ├── download.py     # /download/validate, /download/execute
│   └── history.py      # /history endpoints
├── services/
│   ├── processor.py    # ffmpeg audio processing
│   └── history.py      # JSON-based history management
├── templates/
│   ├── base.html       # Base layout with theme selector
│   ├── index.html      # Main 3-column interface
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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page |
| POST | `/process` | Process audio, returns preview partial |
| POST | `/upload` | Upload file to input directory |
| GET | `/preview/{filename}` | Serve audio file |
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
| light | Subtle ambience | 80 Hz | 6000 Hz | 10\|20 ms |
| medium | Noticeable reverb | 100 Hz | 4500 Hz | 15\|25\|35\|50 ms |
| heavy | Strong cave effect | 120 Hz | 3500 Hz | 20\|35\|55\|80 ms |
| extreme | Deep bunker sound | 150 Hz | 2500 Hz | 25\|45\|70\|100\|140 ms |

## Themes

10 dark themes defined in `static/css/themes.css`:
- Darcula (default), Dracula, Monokai, Nord, Solarized
- Gruvbox, One Dark, Tokyo Night, Catppuccin, Neon

Theme selection via `data-theme` attribute, persisted in localStorage.

## Development Notes

- Source files: `data/input/` (or upload/URL download)
- Output files: `data/output/`
- History: `data/history.json` (max 50 entries)
- Logs: `logs/app.log` (7-day retention)

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
