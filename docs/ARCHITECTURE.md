# Architecture

FFmpeg Sandbox system architecture and component relationships.

## C4 Context Diagram

High-level system boundary showing external dependencies.

```mermaid
%%{init: {'theme': 'dark'}}%%
graph TB
    subgraph External
        User[fa:fa-user User Browser]
        YT[fa:fa-youtube YouTube/Video Sites]
    end

    subgraph FFmpeg Sandbox
        App[fa:fa-server FastAPI Application]
    end

    subgraph System Dependencies
        FFmpeg[fa:fa-film FFmpeg CLI]
        YtDlp[fa:fa-download yt-dlp]
        FS[fa:fa-folder .data/ Storage]
    end

    User -->|HTTP/HTMX| App
    App -->|subprocess| FFmpeg
    App -->|subprocess| YtDlp
    YtDlp -->|download| YT
    App -->|read/write| FS
    FFmpeg -->|output| FS
```

## C4 Container Diagram

Application containers and their interactions.

```mermaid
%%{init: {'theme': 'dark'}}%%
graph LR
    subgraph Docker Container
        subgraph FastAPI
            Main[main.py]
            Audio[routers/audio.py]
            Download[routers/download.py]
            History[routers/history.py]
        end

        subgraph Services
            Processor[processor.py]
            FilterChain[filter_chain.py]
            Executor[ffmpeg_executor.py]
            Settings[settings.py]
        end

        subgraph Templates
            Jinja[Jinja2 Templates]
            Partials[HTMX Partials]
        end
    end

    subgraph Storage
        Input[.data/input/]
        Output[.data/output/]
        Logs[.data/logs/]
    end

    Main --> Audio
    Main --> Download
    Main --> History
    Audio --> Processor
    Processor --> FilterChain
    Processor --> Executor
    Audio --> Settings
    Executor --> Output
    Download --> Input
```

## Component Diagram

Service layer module dependencies.

```mermaid
%%{init: {'theme': 'dark'}}%%
graph TD
    subgraph Routers
        A[audio.py]
        D[download.py]
        H[history.py]
    end

    subgraph Core Services
        P[processor.py]
        FC[filter_chain.py]
        FE[ffmpeg_executor.py]
    end

    subgraph Filter Builders
        FA[filters_audio.py]
        FV[filters_video.py]
    end

    subgraph Data Services
        S[settings.py]
        FM[file_metadata.py]
        HI[history.py]
        M[metadata.py]
    end

    subgraph Preset Services
        PR[presets.py]
        PT[presets_themes.py]
        US[user_shortcuts.py]
    end

    A --> P
    A --> S
    A --> PR
    A --> PT
    D --> DL[downloader.py]
    H --> HI
    H --> S

    P --> FC
    P --> FE
    P --> M
    FC --> FA
    FC --> FV

    S --> FM
    S --> PR
```

## Data Model (ER Diagram)

Core data structures and their relationships.

```mermaid
%%{init: {'theme': 'dark'}}%%
erDiagram
    UserSettings ||--o{ CategorySettings : contains
    UserSettings {
        string active_category
        string active_tab
        list video_theme_chain
        list audio_theme_chain
    }

    CategorySettings {
        string preset
        dict custom_values
    }

    HistoryEntry {
        string id PK
        datetime timestamp
        string input_file
        string output_file
        string start_time
        string end_time
        string volume_preset
        string tunnel_preset
        string frequency_preset
    }

    ThemePreset ||--|{ FilterStep : contains
    ThemePreset {
        string key PK
        string name
        string description
        string icon
    }

    FilterStep {
        string type
        dict params
    }

    PresetConfig {
        string key PK
        string name
        string description
        string preset_category
        bool is_user_shortcut
    }

    FileMetadata {
        string filename PK
        dict source
        dict settings
        list history
    }

    FileMetadata ||--|| UserSettings : stores
    FileMetadata ||--o{ HistoryEntry : tracks
```

## Filter Categories

### Audio Filters (7)

| Category | Service Function | FFmpeg Filter |
|----------|-----------------|---------------|
| Volume | `build_volume_filter()` | `volume={val}` |
| Tunnel | `build_tunnel_filter()` | `aecho=0.8:0.85:{delays}:{decays}` |
| Frequency | `build_frequency_filter()` | `highpass=f={hz},lowpass=f={hz}` |
| Speed | `build_speed_filter()` | `atempo={ratio}` (chained for extremes) |
| Pitch | `build_pitch_filter()` | `asetrate,atempo,aresample` |
| Noise Reduction | `build_noise_reduction_filter()` | `afftdn=nf={floor}:nr={reduction}` |
| Compressor | `build_compressor_filter()` | `acompressor=threshold:ratio:...` |

### Video Filters (6 + 4 theme-only)

| Category | Service Function | FFmpeg Filter |
|----------|-----------------|---------------|
| Brightness | `build_eq_filter()` | `eq=brightness={val}` |
| Contrast | `build_eq_filter()` | `eq=contrast={val}` |
| Saturation | `build_eq_filter()` | `eq=saturation={val}` |
| Blur | `build_blur_filter()` | `gblur=sigma={val}` |
| Sharpen | `build_sharpen_filter()` | `unsharp=5:5:{amount}:5:5:0` |
| Transform | `build_transform_filter()` | `hflip\|vflip\|transpose` |
| Crop | `build_crop_filter()` | `crop=ih*{ratio}:ih` |
| Scale | `build_scale_filter()` | `scale={w}:{h}` |
| Colorshift | `build_colorshift_filter()` | `rgbashift=rh=-{n}:bh={n}` |
| Overlay | `build_overlay_filter()` | `drawtext=...` |

## File System Layout

```
.data/
├── input/
│   ├── video.mp4           # Uploaded/downloaded media
│   └── video.yml           # Per-file metadata + settings + history
├── output/
│   └── processed_*.mp4     # FFmpeg output files
├── logs/
│   └── app.log             # Application logs
├── .user_settings.yml      # Global user preferences
├── user-presets.yml        # Custom user shortcuts
└── history.json            # Processing history index
```

## Request Flow Overview

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant R as Router
    participant S as Services
    participant F as FFmpeg

    B->>R: HTTP Request (HTMX)
    R->>S: Load settings/presets
    S-->>R: UserSettings + PresetConfigs

    alt Processing Request
        R->>S: build_filter_chain()
        S->>F: ffmpeg subprocess
        F-->>S: Output file
        S->>S: add_history_entry()
    end

    R-->>B: HTML Partial Response
    B->>B: HTMX swap into DOM
```
