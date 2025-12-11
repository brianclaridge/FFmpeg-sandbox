# Audio Processor SPA - Implementation Plan

## Overview
Build a Python-based SPA using FastAPI + HTMX that provides a web interface for audio extraction and processing from video files with various effects (tunnel, reverb, echo).

## Technology Stack
- **Backend**: FastAPI (async web framework)
- **Frontend**: HTMX (hypermedia-driven SPA)
- **Templates**: Jinja2
- **Audio Processing**: ffmpeg subprocess
- **Logging**: loguru
- **Package Manager**: uv

## Project Structure
```
.data/src/
├── pyproject.toml
├── CLAUDE.md
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── audio.py         # Audio processing endpoints
│   │   └── history.py       # Processing history endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── processor.py     # ffmpeg audio processing
│   │   └── history.py       # File history management
│   ├── templates/
│   │   ├── base.html        # Base template with HTMX
│   │   ├── index.html       # Main processor page
│   │   └── partials/
│   │       ├── preset_form.html
│   │       ├── slider_form.html
│   │       ├── preview.html
│   │       └── history.html
│   └── static/
│       └── css/
│           └── styles.css
└── data/
    ├── input/               # Source video files
    └── output/              # Processed audio files
```

## Features Implementation

### 1. Preset Effects System
- Light tunnel: subtle ambience
- Medium tunnel: noticeable reverb
- Heavy tunnel: strong cave effect
- Extreme tunnel: deep bunker sound

### 2. Custom Parameter Sliders
- Volume (0.5x - 4x)
- High-pass frequency (50Hz - 500Hz)
- Low-pass frequency (2000Hz - 8000Hz)
- Echo delays (10ms - 100ms)
- Echo decay (0.1 - 0.5)

### 3. Audio Preview
- HTML5 audio player
- Real-time playback of processed file

### 4. Processing History
- JSON-based file tracking
- Display previous outputs with parameters
- Re-apply settings from history

## TODO List

1. [ ] Create project structure and pyproject.toml
2. [ ] Implement FastAPI app with Jinja2 templates
3. [ ] Build audio processor service (ffmpeg subprocess)
4. [ ] Create preset definitions and models
5. [ ] Implement HTMX-powered form with presets
6. [ ] Add custom parameter sliders
7. [ ] Implement audio preview endpoint
8. [ ] Build processing history service
9. [ ] Create history display partial
10. [ ] Add logging with loguru
11. [ ] Write CLAUDE.md documentation
12. [ ] Write README.md with usage instructions

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Main page with processor form |
| POST | /process | Process audio with parameters |
| GET | /preview/{filename} | Serve processed audio file |
| GET | /history | Get processing history |
| DELETE | /history/{id} | Remove history entry |
| GET | /partials/sliders | Get slider form partial |

## ffmpeg Command Template
```bash
ffmpeg -y -i {input} -ss {start} -to {end} \
  -af "volume={vol},highpass=f={hp},lowpass=f={lp},aecho={in_gain}:{out_gain}:{delays}:{decays}" \
  -vn {output}
```
