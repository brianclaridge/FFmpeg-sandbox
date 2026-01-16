# FFmpeg Sandbox

Audio/video processing app with 13 filter categories and YAML-driven presets.

## Tech Stack

FastAPI | HTMX | Jinja2 | FFmpeg | yt-dlp | uv (Astral)

## Quick Start

```bash
task rebuild          # After every change (cleans, rebuilds, restarts)
uv sync               # Install dependencies
docker compose up -d  # Start container
```

## Documentation

| Doc | Description |
|-----|-------------|
| [Getting Started](docs/GETTING_STARTED.md) | Installation, requirements, usage guide |
| [Filters Reference](docs/FILTERS.md) | Audio/video filter categories and presets |
| [Architecture](docs/ARCHITECTURE.md) | C4 diagrams, ER model, component graph |
| [API Reference](docs/API_REFERENCE.md) | All 28 endpoints with HTMX triggers |
| [Processing Flow](docs/PROCESSING_FLOW.md) | Sequence diagrams and state machines |
| [HTMX Patterns](docs/HTMX_PATTERNS.md) | Swap strategies and event patterns |
| [Project Structure](docs/PROJECT_STRUCTURE.md) | Directory tree and file purposes |
| [Stack](docs/STACK.md) | Technology stack details and rationale |
| [Common Tasks](docs/COMMON_TASKS.md) | How-to guides for development |
| [Roadmap](docs/ROADMAP.md) | Development phases and feature priorities |

## Key Files

| File | Purpose |
|------|---------|
| `presets.yml` | 66 filter shortcuts across 13 categories |
| `presets_themes.yml` | 12 themed transformation presets |
| `config.yml` | Application configuration |
| `Taskfile.yml` | Task runner commands |
