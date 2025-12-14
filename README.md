# FFmpeg-sandbox

> **NOTICE:** This is a sample application created with the assistance of my opinionated [.claude](https://github.com/brianclaridge/.claude) stack. It's not meant to be used in production, operated for profit, etc. See [LICENSE.md](./LICENSE.md) for more information.

A web-based audio/video processing tool with 13 filter categories and YAML-driven presets.

## Features

- **13 filter categories** with 66 presets across audio and video
- **Audio filters:** Volume, Tunnel (echo), Frequency, Speed, Pitch, Noise Reduction, Compressor
- **Video filters:** Brightness, Contrast, Saturation, Blur, Sharpen, Transform
- **YAML-driven presets** via `presets.yml` - customize without code changes
- **Per-file metadata** storing settings in `.data/input/{filename}.yml`
- **Dual-handle clip range slider** with millisecond precision
- **Draggable video preview modal** for video files
- **URL download** via yt-dlp (YouTube, etc.)
- **10 dark themes** including Nord, Tokyo Night, Catppuccin, and more
- **Configurable via `config.yml`**

## Requirements

Docker (recommended):
```bash
docker compose up -d
# Open http://localhost:8000
```

Or local install:
- Python 3.12+
- ffmpeg (must be in PATH)
- yt-dlp (for URL downloads)
- uv (Astral package manager)

## Installation

```bash
git clone git@github.com:brianclaridge/FFmpeg-sandbox.git
cd FFmpeg-sandbox
uv sync
uv run python -m app.main
```

## Usage

1. **Add source files** via upload, drag-and-drop, or URL download
2. **Select clip range** using the dual-handle slider
3. **Choose filter presets** from Audio/Video tabs
4. **Click Process** to generate output
5. **Preview and download** the result

## Filter Categories

### Audio Filters

| Category | Presets | Description |
|----------|---------|-------------|
| Volume | None, 0.25x-4x | Gain control (mute to 4x boost) |
| Tunnel | None, Subtle, Medium, Heavy, Extreme | Echo/reverb effects |
| Frequency | Flat, Bass Cut, Treble Cut, Narrow, Voice | High/low-pass filtering |
| Speed | 0.5x-2x | Playback speed adjustment |
| Pitch | Low, Normal, High, Chipmunk | Pitch shifting (semitones) |
| Noise Reduction | None, Light, Medium, Heavy | Background noise removal |
| Compressor | None, Light, Podcast, Broadcast | Dynamic range control |

### Video Filters

| Category | Presets | Description |
|----------|---------|-------------|
| Brightness | Dark, Normal, Bright | Image brightness |
| Contrast | Low, Normal, High | Image contrast |
| Saturation | Grayscale, Muted, Normal, Vivid | Color saturation |
| Blur | None, Light, Medium, Heavy | Gaussian blur |
| Sharpen | None, Light, Medium, Strong | Edge enhancement |
| Transform | Flip H/V, Rotate 90/180/270 | Geometric transforms |

## Customizing Presets

Edit `presets.yml` to add or modify presets:

```yaml
audio:
  volume:
    custom:
      name: "Custom"
      description: "My custom preset"
      volume: 2.5
```

Restart container after changes. Presets are validated on startup.

## Themes

10 dark themes: Darcula (default), Dracula, Monokai, Nord, Solarized, Gruvbox, One Dark, Tokyo Night, Catppuccin, Neon

Theme selection saved in localStorage.

## Project Structure

```text
Root Files:
├── config.yml           # App configuration
├── presets.yml          # Filter presets (66 presets, 13 categories)
├── Dockerfile           # Container build
├── docker-compose.yml   # Container orchestration
├── Taskfile.yml         # Task runner commands
└── pyproject.toml       # Python dependencies (uv)

.data/
├── input/               # Source files + per-file metadata
├── output/              # Processed files
└── logs/                # App logs

app/
├── main.py              # FastAPI entry point
├── config.py            # Config loader
├── models.py            # Pydantic schemas (240 lines)
├── routers/
│   ├── audio.py         # Processing endpoints
│   ├── download.py      # yt-dlp endpoints
│   └── history.py       # History endpoints
├── services/
│   ├── presets.py       # YAML preset loader
│   ├── processor.py     # FFmpeg orchestration
│   ├── metadata.py      # File introspection
│   ├── filters_audio.py # Audio filter builders
│   ├── filters_video.py # Video filter builders
│   ├── filter_chain.py  # Filter aggregation
│   ├── ffmpeg_executor.py # Subprocess wrapper
│   ├── downloader.py    # yt-dlp downloading
│   ├── file_metadata.py # Per-file metadata
│   ├── history.py       # Processing history
│   └── settings.py      # User settings
├── templates/
│   ├── base.html        # Layout + themes
│   ├── index.html       # Main interface
│   └── partials/        # 10 HTMX partials
└── static/css/          # 10 modular CSS files
```

## License

See [LICENSE.md](./LICENSE.md)
