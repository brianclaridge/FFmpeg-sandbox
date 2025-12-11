# CLAUDE.md - Audio Processor SPA

## Project Overview

A Python-based Single Page Application for extracting and processing audio from video files with tunnel/reverb effects. Built with FastAPI and HTMX for a dynamic, server-rendered experience.

## Tech Stack

- **Backend**: FastAPI 0.115+
- **Frontend**: HTMX 2.0+ (hypermedia-driven)
- **Templates**: Jinja2
- **Audio**: ffmpeg (subprocess)
- **Logging**: loguru
- **Package Manager**: uv (Astral)

## Project Structure

```
src/
├── pyproject.toml          # Project dependencies and metadata
├── app/
│   ├── main.py             # FastAPI entry point, routes index
│   ├── config.py           # Path configuration
│   ├── models.py           # Pydantic models, preset definitions
│   ├── routers/
│   │   ├── audio.py        # /process, /preview, /partials/sliders
│   │   └── history.py      # /history endpoints
│   ├── services/
│   │   ├── processor.py    # ffmpeg audio processing
│   │   └── history.py      # JSON-based history management
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS assets
└── data/
    ├── input/              # Source video/audio files
    └── output/             # Processed audio files
```

## Key Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python -m app.main

# Or use the entry point
uv run audio-processor
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page |
| POST | `/process` | Process audio, returns preview partial |
| GET | `/preview/{filename}` | Serve audio file |
| GET | `/partials/sliders?preset=` | Get slider form for preset |
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

## Development Notes

- Place source files in `data/input/` before processing
- Processed files are saved to `data/output/`
- History is stored in `data/history.json` (max 50 entries)
- Logs are written to `logs/app.log` with 7-day retention

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

### Modify the filter chain

Edit `app/services/processor.py` in the `process_audio` function.

### Add new form fields

1. Add field to `ProcessRequest` in `models.py`
2. Add HTML input in `templates/index.html`
3. Add handling in `routers/audio.py`
