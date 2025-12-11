# FFmpeg-sandbox

A web-based audio extraction and processing tool with tunnel/reverb effects.

## Features

- Extract audio segments from video files
- Apply tunnel/cave acoustic effects
- Four effect presets (Light, Medium, Heavy, Extreme)
- Custom parameter sliders for fine-tuning
- In-browser audio preview and playback
- Processing history with one-click reapply
- **File upload** with drag-and-drop support
- **URL download** via yt-dlp (YouTube, etc.)
- **10 dark themes** including Darcula, Dracula, Nord, Tokyo Night, and more

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

## Effect Presets

| Preset | Effect | Best For |
|--------|--------|----------|
| Light | Subtle ambience | Natural-sounding reverb |
| Medium | Noticeable tunnel | Standard tunnel effect |
| Heavy | Strong cave echo | Dramatic atmosphere |
| Extreme | Deep bunker | Heavily processed sound |

## Custom Parameters

- **Volume**: 0.5x - 4x amplification
- **High-pass**: 50-500 Hz (removes low rumble)
- **Low-pass**: 2000-8000 Hz (controls high frequency cutoff)
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

## Project Structure

```text
app/
├── main.py              # Application entry point
├── config.py            # Path configuration
├── models.py            # Data models and presets
├── routers/
│   ├── audio.py         # /process, /preview, /upload
│   ├── download.py      # /download URL endpoints
│   └── history.py       # /history endpoints
├── services/
│   ├── processor.py     # ffmpeg audio processing
│   └── history.py       # JSON-based history management
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Base layout with theme selector
│   ├── index.html       # Main 3-column interface
│   └── partials/        # HTMX partial templates
└── static/
    └── css/
        ├── themes.css   # 10 dark theme definitions
        └── styles.css   # Component styles
```

## License

MIT
