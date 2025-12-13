# Stack

## Frontend

- **HTMX** - Dynamic interactions without JavaScript frameworks
- **Jinja2 templates** - Server-side rendering with partials
- **CSS custom properties** - 10 dark themes (Nord, Darcula, Dracula, Monokai, etc.)
- **Font Awesome** - Icon library for UI elements

## Backend

- **Python 3.12** - Runtime
- **FastAPI** - Async API framework with automatic OpenAPI docs
- **Pydantic** - Request/response validation and data models
- **Loguru** - Structured logging with rotation
- **PyYAML** - Configuration and per-file metadata storage

## Audio/Video Processing

- **ffmpeg** - Audio extraction, filtering (volume, highpass, lowpass, echo)
- **yt-dlp** - URL downloading with metadata extraction (title, uploader, tags, filesize)

## DevOps

- **Docker + Docker Compose** - Containerized deployment
- **uv (Astral)** - Fast Python package management
- **Taskfile** - Task runner for build/clean/rebuild workflows

## Architecture

### 4-Column Layout

1. **Source** - File selection, upload, URL download, file metadata display
2. **Clip Selection + Effect Chain** - Dual-handle range slider, Volume/Tunnel/Frequency accordion
3. **History** - Processing history with replay capability
4. **Preview** - Inline video player, processed audio playback

### Per-File Metadata

Each input file gets a companion `.yml` with:

- Source info (title, uploader, URL, tags) from yt-dlp
- Effect chain settings (volume/tunnel/frequency presets)
- Processing history

### Effect Chain Categories

- **Volume**: None (passthrough), 1x, 1.5x, 2x, 3x, 4x
- **Tunnel**: None, Subtle, Medium, Heavy, Extreme (echo/reverb)
- **Frequency**: Flat, Bass Cut, Treble Cut, Narrow Band, Voice Clarity

## Rationale

This stack prioritizes simplicity and server-side rendering. HTMX enables dynamic interactions without JavaScript frameworks, keeping the frontend as HTML partials rendered by Jinja2. FastAPI provides a modern async Python backend with automatic OpenAPI docs and Pydantic validation.

The audio pipeline uses industry-standard tools: ffmpeg for processing and yt-dlp for URL downloads. Docker ensures reproducible deployments while uv handles fast Python dependency management.

## Stack Maturity

**Verdict: Well-supported, pragmatic, not antiquated.**

| Component | Status | Notes |
|-----------|--------|-------|
| **FastAPI** | Active, growing | Released 2018, now dominant Python API framework. Async-first, excellent docs. |
| **HTMX** | Active, gaining traction | 2020 revival of hypermedia. Small but passionate community. Production-ready. |
| **Jinja2** | Mature, stable | Battle-tested since 2008. Not "exciting" but extremely reliable. |
| **ffmpeg** | Industry standard | 20+ years. The definitive audio/video tool. Not going anywhere. |
| **Docker** | Ubiquitous | Standard containerization. Some movement toward Podman but Docker remains dominant. |
| **uv** | New, high momentum | 2024 release from Astral. Rapidly becoming the preferred Python toolchain. |
| **yt-dlp** | Active, well-maintained | Fork of youtube-dl with active development and broad site support. |

This stack avoids both bleeding-edge risk and legacy debt. HTMX is the only "opinionated" choice—it bets on hypermedia over SPA frameworks, which may require explanation to developers expecting React/Vue. Everything else is mainstream or ascending.

## Modern Alternatives

For a more 2025-idiomatic approach: swap HTMX for **Inertia.js** with a **React/Vue** frontend for richer interactivity while keeping server-driven routing. Replace Jinja2 with **Templ** (Go) or keep Python but use **Litestar** instead of FastAPI for better performance.

Consider **Bun** for JavaScript tooling if adding a build step. For containerization, **Podman** offers rootless containers. **Rye** competes with uv but uv has momentum. For audio, **Remotion** could enable browser-based video/audio editing without ffmpeg subprocess calls.
