# Project Structure

FFmpeg Sandbox directory layout and file purposes.

## Root Files

```
├── config.yml           # App configuration
├── presets.yml          # Filter shortcuts (66 shortcuts, 13 categories)
├── presets_themes.yml   # Theme presets (12 presets: 6 video, 6 audio)
├── Dockerfile           # Container build
├── docker-compose.yml   # Container orchestration
├── docker-entrypoint.sh # Container startup script
├── Taskfile.yml         # Task runner commands
├── pyproject.toml       # Python dependencies (uv)
└── scripts/             # Development utilities
    ├── debug-path.ps1
    ├── diagnose-logs.ps1
    ├── docker-compose-wrapper.ps1
    ├── health-check.ps1
    ├── setup-dirs.ps1
    └── test-ytdlp.ps1
```

## Data Directory

```
.data/
├── input/               # Source files + per-file .yml metadata
├── output/              # Processed files
└── logs/                # App logs
```

## Application Code

```
app/
├── main.py              # FastAPI entry, index route
├── config.py            # Config loader
├── models.py            # Pydantic schemas (290 lines)
├── routers/
│   ├── audio.py         # /process, /preview, filter chain endpoints
│   ├── download.py      # yt-dlp download endpoints
│   └── history.py       # History endpoints
├── services/
│   ├── __init__.py      # Public API exports
│   ├── presets.py       # YAML shortcut loader with Pydantic validation
│   ├── presets_themes.py # Theme preset loader (VHS, Vinyl, etc.)
│   ├── user_shortcuts.py # User shortcut CRUD operations
│   ├── processor.py     # FFmpeg processing orchestration
│   ├── metadata.py      # File introspection (duration, codecs)
│   ├── filters_audio.py # Audio filter builders
│   ├── filters_video.py # Video filter builders
│   ├── filter_chain.py  # Filter chain aggregation
│   ├── ffmpeg_executor.py # Subprocess wrapper
│   ├── downloader.py    # yt-dlp downloading
│   ├── file_metadata.py # Per-file YAML metadata
│   ├── history.py       # Processing history
│   └── settings.py      # User settings persistence
```

## Templates

```
├── templates/
│   ├── base.html        # Layout + theme selector
│   ├── index.html       # Main interface
│   └── partials/        # 15 HTMX partials
│       ├── download_complete.html        # Download success message
│       ├── download_status.html          # Download progress
│       ├── filters_audio_accordion.html  # Audio filter UI (shortcuts)
│       ├── filters_presets_accordion.html # Theme presets UI
│       ├── filters_tabs.html             # Audio/Video/Presets tab switcher
│       ├── filters_video_accordion.html  # Video filter UI (shortcuts)
│       ├── history.html                  # Processing history list
│       ├── history_preview.html          # History item preview
│       ├── import_result.html            # Shortcut import feedback
│       ├── preset_management.html        # Preset management UI
│       ├── preview.html                  # Audio/video preview player
│       ├── processing_modal.html         # Processing progress modal
│       ├── save_shortcut_modal.html      # Save shortcut dialog
│       ├── slider_form.html              # Clip range slider
│       └── upload_status.html            # File upload feedback
```

## Stylesheets

```
└── static/css/
    ├── base.css         # CSS reset, variables
    ├── buttons.css      # Button components
    ├── components.css   # Reusable UI components
    ├── filter-chain.css # Filter chain styling
    ├── forms.css        # Form elements
    ├── layout.css       # Page layout, grid
    ├── media.css        # Audio/video player styles
    ├── modal.css        # Modal dialogs
    ├── styles.css       # Main stylesheet (imports)
    └── themes.css       # 10 dark themes
```
