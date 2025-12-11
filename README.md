# Audio Processor

A web-based audio extraction and processing tool with tunnel/reverb effects.

## Features

- Extract audio segments from video files
- Apply tunnel/cave acoustic effects
- Four effect presets (Light, Medium, Heavy, Extreme)
- Custom parameter sliders for fine-tuning
- In-browser audio preview
- Processing history with one-click reapply

## Requirements

- Python 3.11+
- ffmpeg (must be in PATH)
- uv (Astral package manager)

Or use Docker (recommended):

- Docker
- Docker Compose

## Docker (Recommended)

```bash
# Add source files to data/input/
cp your-video.mp4 data/input/

# Build and run
docker compose up -d

# Open http://localhost:8000

# Processed files appear in data/output/
```

## Installation

```bash
# Clone
git clone git@github.com:brianclaridge/audio-clip-helper.git

# navigate to project
cd ./audio-clip-helper

# Install dependencies
uv sync
```

## Usage

### 1. Add source files

Place video or audio files in the `data/input/` directory:

```bash
cp your-video.mp4 data/input/
```

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

1. Select a source file from the dropdown
2. Set start and end times (format: `HH:MM:SS` or `HH:MM:SS.mmm`)
3. Choose a preset (Light, Medium, Heavy, Extreme)
4. Optionally adjust sliders for custom parameters
5. Click "Process Audio"
6. Preview the result in the browser
7. Download if satisfied

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

# Get processing history
curl http://localhost:8000/history

# Download processed file
curl -O http://localhost:8000/preview/processed_20241210_120000.mp3
```

## Project Structure

```text
src/
├── app/
│   ├── main.py           # Application entry point
│   ├── models.py         # Data models and presets
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── templates/        # Jinja2 HTML templates
│   └── static/           # CSS assets
├── data/
│   ├── input/            # Source files
│   └── output/           # Processed files
└── logs/                 # Application logs
```

## License

MIT
