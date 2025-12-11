# Stack

## Frontend

- HTMX
- Jinja2 templates
- CSS custom properties (theming)

## Backend

- Python
- FastAPI
- Pydantic
- Loguru

## Audio Processing

- ffmpeg
- yt-dlp

## DevOps

- Docker
- Docker Compose
- uv (Astral)

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

This stack avoids both bleeding-edge risk and legacy debt. HTMX is the only "opinionated" choice—it bets on hypermedia over SPA frameworks, which may require explanation to developers expecting React/Vue. Everything else is mainstream or ascending.

## Modern Alternatives

For a more 2025-idiomatic approach: swap HTMX for **Inertia.js** with a **React/Vue** frontend for richer interactivity while keeping server-driven routing. Replace Jinja2 with **Templ** (Go) or keep Python but use **Litestar** instead of FastAPI for better performance.

Consider **Bun** for JavaScript tooling if adding a build step. For containerization, **Podman** offers rootless containers. **Rye** competes with uv but uv has momentum. For audio, **Remotion** could enable browser-based video/audio editing without ffmpeg subprocess calls.
