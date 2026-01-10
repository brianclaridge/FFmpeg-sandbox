# FFmpeg Sandbox

Audio/video processing app with 13 filter categories and YAML-driven presets.

## Quick Start

```bash
task rebuild          # After every change (cleans, rebuilds, restarts)
uv sync               # Install dependencies
docker compose up -d  # Start container
```

## Tech Stack

FastAPI | HTMX | Jinja2 | FFmpeg | yt-dlp | uv (Astral)

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/ROADMAP.md](docs/ROADMAP.md) | Development phases and feature priorities |
| [docs/STACK.md](docs/STACK.md) | Technology stack details |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Directory tree and file purposes |
| [docs/FILTERS.md](docs/FILTERS.md) | Audio/video filter categories and presets |
| [docs/COMMON_TASKS.md](docs/COMMON_TASKS.md) | How-to guides for development |

## Key Files

| File | Purpose |
|------|---------|
| `presets.yml` | 66 filter shortcuts across 13 categories |
| `presets_themes.yml` | 12 themed transformation presets |
| `config.yml` | Application configuration |
| `Taskfile.yml` | Task runner commands |

## Filter Categories

**Audio (7):** Volume, Tunnel, Frequency, Speed, Pitch, Noise Reduction, Compressor

**Video (6):** Brightness, Contrast, Saturation, Blur, Sharpen, Transform

See [docs/FILTERS.md](docs/FILTERS.md) for details.
