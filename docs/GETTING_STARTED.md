# Getting Started

Quick start guide for FFmpeg Sandbox.

## Requirements

### Docker (Recommended)

```bash
docker compose up -d
# Open http://localhost:8000
```

### Local Install

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

## Quick Start

```bash
task rebuild          # After every change (cleans, rebuilds, restarts)
uv sync               # Install dependencies
docker compose up -d  # Start container
```

## Usage

1. **Add source files** via upload, drag-and-drop, or URL download
2. **Select clip range** using the dual-handle slider
3. **Choose filter presets** from Audio/Video tabs
4. **Click Process** to generate output
5. **Preview and download** the result

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

10 dark themes available:

- Darcula
- Dracula
- Monokai
- Nord
- Solarized
- Gruvbox
- One Dark
- Tokyo Night
- Catppuccin
- Neon (default)

Theme selection saved in localStorage.

## Next Steps

- [Filters Reference](FILTERS.md) - All filter categories and presets
- [Common Tasks](COMMON_TASKS.md) - Development how-to guides
- [Architecture](ARCHITECTURE.md) - System design and diagrams
