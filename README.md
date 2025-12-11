# FFmpeg-sandbox

> **NOTICE:** This is a sample application created with the assistance of my opinionated [.claude](https://github.com/brianclaridge/.claude) stack. It's not meant to be used in production, operated for profit, etc. See [LICENSE.md](./LICENSE.md) for more information.

A web-based audio extraction and processing tool with visual effect chains.

## Features

- Extract audio segments from video files
- **Visual effect chain** with three processing stages: Volume → Tunnel → Frequency
- Per-category presets with independent controls
- **Per-file metadata** storing settings, history, and source info in `.data/input/{filename}.yml`
- **File metadata display** showing duration, size, codecs, resolution, and bitrate
- **Dual-handle clip range slider** with millisecond precision (defaults to full file)
- **Play/pause/stop controls** for clip preview
- **Draggable video preview modal** for video files
- In-browser audio preview and playback
- Processing history with one-click reapply
- **File upload** with drag-and-drop support
- **URL download** via yt-dlp (YouTube, etc.)
- **10 dark themes** including Darcula, Dracula, Nord, Tokyo Night, and more
- **Configurable via `config.yml`**

## Requirements

- Python 3.11+
- ffmpeg (must be in PATH)
- yt-dlp (for URL downloads)
- uv (Astral package manager)

Or use Docker (recommended):

- Docker
- Docker Compose

## Docker (Recommended)

```bash
# Build and run
docker compose up -d

# Open http://localhost:8000

# Processed files appear in .data/output/
```

## Installation

```bash
# Clone
git clone git@github.com:brianclaridge/audio-clip-helper.git

# Navigate to project
cd ./audio-clip-helper

# Install dependencies
uv sync
```

## Usage

### 1. Add source files

You can add source files in three ways:

**Option A: Copy to input folder**
```bash
cp your-video.mp4 data/input/
```

**Option B: Upload via web interface**
- Click the upload zone or drag-and-drop files

**Option C: Download from URL**
- Paste a YouTube or other supported URL
- Click "Check URL" to validate
- Click "Download" to fetch the file

Downloaded files are saved with anonymized names: `{source}-{id}.{ext}`

| Source | Prefix | Example |
|--------|--------|---------|
| YouTube | `yt` | `yt-dQw4w9WgXcQ.mp4` |
| Twitch | `tw` | `tw-1234567890.mp4` |
| Twitter/X | `x` | `x-1234567890.mp4` |
| TikTok | `tt` | `tt-7123456789.mp4` |
| Other | `dl` | `dl-a1b2c3d4e5f6.mp4` |

Each downloaded file gets a companion `.yml` metadata file containing:
- Original URL, title, uploader, duration
- Effect chain settings (presets per category)
- Processing history with timestamps and parameters

### 2. Start the server

```bash
uv run python -m app.main
```

Or use the installed command:

```bash
uv run audio-processor
```

### 3. Open the web interface

Navigate to `http://localhost:8000` in your browser.

### 4. Process audio

1. Select a source file, upload one, or download from URL
2. Set start and end times (format: `HH:MM:SS` or `HH:MM:SS.mmm`)
3. Choose a preset (Light, Medium, Heavy, Extreme)
4. Optionally adjust sliders for custom parameters
5. Click "Process Audio"
6. Preview the result in the browser
7. Download if satisfied

## Themes

The app includes 10 dark themes selectable from the header dropdown:

| Theme | Description |
|-------|-------------|
| Darcula | JetBrains IDE theme (default) |
| Dracula | Popular purple-accented theme |
| Monokai | Sublime Text classic |
| Nord | Arctic blue palette |
| Solarized | Ethan Schoonover's dark theme |
| Gruvbox | Retro groove colors |
| One Dark | Atom editor theme |
| Tokyo Night | Japanese city lights |
| Catppuccin | Mocha variant |
| Neon | Vibrant pink/blue |

Theme preference is saved in localStorage.

## Effect Chain

The audio processing pipeline consists of three stages, each with independent presets:

### Volume Presets

| Preset | Multiplier | Description |
|--------|------------|-------------|
| 1x | 1.0 | Original volume |
| 1.5x | 1.5 | Slight boost |
| 2x | 2.0 | Double volume |
| 3x | 3.0 | Triple volume |
| 4x | 4.0 | Maximum boost |

### Tunnel Presets

| Preset | Effect | Description |
|--------|--------|-------------|
| None | No echo | Clean audio pass-through |
| Subtle | Light ambience | Gentle room reverb |
| Medium | Noticeable reverb | Standard tunnel effect |
| Heavy | Strong cave echo | Dramatic atmosphere |
| Extreme | Deep bunker | Heavily processed sound |

### Frequency Presets

| Preset | High-pass | Low-pass | Description |
|--------|-----------|----------|-------------|
| Flat | 20 Hz | 20 kHz | Full spectrum |
| Bass Cut | 200 Hz | 20 kHz | Remove low frequencies |
| Treble Cut | 20 Hz | 4 kHz | Remove high frequencies |
| Narrow Band | 150 Hz | 3.5 kHz | Voice-focused range |
| Voice Clarity | 100 Hz | 6 kHz | Optimal for speech |

## Custom Parameters

Within each category, you can fine-tune:

- **Volume**: 0.5x - 4x amplification
- **High-pass**: 20-500 Hz (removes low rumble)
- **Low-pass**: 2000-20000 Hz (controls high frequency cutoff)
- **Delays**: Echo timing in milliseconds (pipe-separated)
- **Decays**: Echo decay factors 0-1 (pipe-separated)

## API

The application exposes a REST API:

```bash
# Process audio
curl -X POST http://localhost:8000/process \
  -F "input_file=video.mp4" \
  -F "start_time=00:00:00" \
  -F "end_time=00:00:06" \
  -F "preset=medium"

# Upload a file
curl -X POST http://localhost:8000/upload \
  -F "file=@your-video.mp4"

# Validate a URL
curl -X POST http://localhost:8000/download/validate \
  -F "download_url=https://youtube.com/watch?v=..."

# Get processing history
curl http://localhost:8000/history

# Download processed file
curl -O http://localhost:8000/preview/processed_20241210_120000.mp3
```

## Configuration

The application is configurable via `config.yml`:

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

## Project Structure

```text
config.yml               # Application configuration
.data/
├── input/               # Source files + per-file .yml metadata
│   ├── yt-abc123.mp4    # Downloaded video (anonymized name)
│   └── yt-abc123.yml    # Settings, history, source info
├── output/              # Processed audio files
└── logs/                # Application logs
app/
├── main.py              # Application entry point
├── config.py            # Config loader with dataclasses
├── models.py            # Data models, presets, and enums
├── routers/
│   ├── audio.py         # /process, /preview, /upload, effect chain endpoints
│   ├── download.py      # /download URL endpoints
│   └── history.py       # /history endpoints
├── services/
│   ├── processor.py     # ffmpeg audio processing + file metadata
│   ├── downloader.py    # yt-dlp video downloading
│   ├── file_metadata.py # Per-file YAML metadata service
│   ├── history.py       # Processing history (per-file)
│   └── settings.py      # Effect chain settings (per-file)
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Base layout with theme selector
│   ├── index.html       # Main 3-column interface
│   └── partials/        # HTMX partial templates
│       ├── effect_chain.html
│       ├── effect_chain_boxes.html
│       ├── panel_volume.html
│       ├── panel_tunnel.html
│       └── panel_frequency.html
└── static/
    └── css/
        ├── themes.css   # 10 dark theme definitions
        └── styles.css   # Component styles
```

## License

See [LICENSE.md](./LICENSE.md)
