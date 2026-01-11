# Processing Flow

Sequence diagrams and state machines for FFmpeg Sandbox operations.

## Application State Machine

```mermaid
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> Idle: Page Load

    Idle --> FileSelected: Upload/Download complete
    FileSelected --> Idle: Clear selection

    FileSelected --> ConfiguringFilters: Adjust sliders
    ConfiguringFilters --> FileSelected: Settings saved

    FileSelected --> Processing: Click Process
    Processing --> Complete: FFmpeg success
    Processing --> Error: FFmpeg failure

    Complete --> FileSelected: Process another
    Complete --> Previewing: Auto-play output
    Previewing --> FileSelected: Close preview

    Error --> FileSelected: Dismiss error
    Error --> Processing: Retry
```

## Upload Flow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as FastAPI
    participant M as metadata.py
    participant FS as File System

    U->>B: Select file
    B->>F: POST /upload (multipart)
    F->>FS: Save to .data/input/
    F->>M: get_file_metadata()
    M->>FS: ffprobe file
    FS-->>M: Duration, codec, etc.
    M->>FS: Create {file}.yml
    F-->>B: upload_status.html
    B->>B: HTMX swap #upload-status
    B->>F: GET /duration/{file}
    F-->>B: Metadata JSON
    B->>B: Update slider range
    B->>F: GET /partials/filter-chain
    F-->>B: filters_tabs.html
    B->>B: HTMX swap #filters-area
```

## Processing Flow (Synchronous)

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant R as audio.py
    participant S as settings.py
    participant P as presets.py
    participant FC as filter_chain.py
    participant PR as processor.py
    participant FF as FFmpeg
    participant H as history.py

    B->>R: POST /process
    R->>S: load_user_settings(filename)
    S-->>R: UserSettings

    R->>P: get_*_presets()
    P-->>R: Preset dictionaries

    R->>FC: build_audio_filter_chain()
    FC-->>R: "-af volume=1.5,atempo=2.0"

    R->>FC: build_video_filter_chain()
    FC-->>R: "-vf eq=brightness=0.1"

    R->>PR: process_video_with_filters()
    PR->>FF: subprocess.run(ffmpeg_cmd)
    FF-->>PR: Exit code 0
    PR-->>R: output_file

    R->>H: add_history_entry()
    H-->>R: Entry saved

    R-->>B: preview.html
    B->>B: HTMX swap #preview-area
```

## Processing Flow (SSE Progress)

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant M as Modal JS
    participant R as audio.py
    participant PR as processor.py
    participant FF as FFmpeg

    B->>M: Click Process button
    M->>M: Show modal
    M->>R: GET /process-with-progress (SSE)

    R->>PR: process_video_with_progress()

    loop Every 100ms
        PR->>FF: Read stderr
        FF-->>PR: "time=00:00:05.00"
        PR-->>R: yield progress
        R-->>M: event: progress {percent: 50}
        M->>M: Update progress bar
    end

    FF-->>PR: Exit code 0
    PR-->>R: yield complete
    R-->>M: event: complete {output_file}
    M->>M: Close modal
    M->>B: Trigger history refresh
    B->>R: GET /history
    R-->>B: history.html
```

## Filter Chain Building

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TD
    A[Start] --> B{Get UserSettings}
    B --> C[For each category]

    C --> D{Has custom_values?}
    D -->|Yes| E[Use custom_values]
    D -->|No| F{Preset != none?}
    F -->|Yes| G[Lookup preset config]
    F -->|No| H[Skip filter]

    E --> I[Build filter string]
    G --> I
    H --> J{More categories?}
    I --> J

    J -->|Yes| C
    J -->|No| K[Join with commas]
    K --> L[Return filter chain]
```

## Audio Filter Chain Order

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    subgraph Audio Pipeline
        A[Input] --> V[Volume]
        V --> F[Frequency]
        F --> T[Tunnel/Echo]
        T --> S[Speed]
        S --> P[Pitch]
        P --> N[Noise Reduction]
        N --> C[Compressor]
        C --> O[Output]
    end
```

**Filter String Example:**
```
volume=1.5,highpass=f=100,lowpass=f=8000,aecho=0.8:0.85:60:0.3,atempo=2.0,afftdn=nf=-25:nr=50,acompressor=threshold=-20dB:ratio=4
```

## Video Filter Chain Order

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    subgraph Video Pipeline
        A[Input] --> CR[Crop]
        CR --> SC[Scale]
        SC --> CS[Colorshift]
        CS --> EQ[EQ]
        EQ --> BL[Blur]
        BL --> SH[Sharpen]
        SH --> TR[Transform]
        TR --> SP[Speed]
        SP --> OV[Overlay]
        OV --> O[Output]
    end
```

**Filter String Example:**
```
crop=ih*16/9:ih,scale=1280:720,eq=brightness=0.1:contrast=1.2:saturation=0.9,gblur=sigma=0.5,unsharp=5:5:0.3:5:5:0,hflip
```

## Theme Preset Application

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant R as audio.py
    participant S as settings.py
    participant PT as presets_themes.py

    B->>R: POST /toggle-theme-preset/video/vhs_playback
    R->>S: load_user_settings()
    S-->>R: UserSettings

    R->>PT: get_video_theme_presets()
    PT-->>R: {vhs_playback: ThemePreset}

    R->>R: Add to video_theme_chain

    loop For each filter in preset
        R->>S: update_category_custom_values()
        Note right of S: saturation.custom_values = {saturation: 1.3}
    end

    R->>S: save_user_settings()
    R-->>B: presets_accordion.html
```

## Theme Preset Filter Priority

When multiple theme presets are chained, filters are applied in order. **Last preset wins** for conflicting filters.

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TD
    subgraph Chain: VHS + Film Grain
        A[VHS Playback] --> B[saturation: 1.3]
        A --> C[contrast: 1.2]
        A --> D[blur: 0.5]

        E[Film Grain] --> F[saturation: 0.9]
        E --> G[contrast: 1.1]
        E --> H[sharpen: 0.3]
    end

    subgraph Final Values
        B -.->|Overwritten| F
        C -.->|Overwritten| G
        D --> I[blur: 0.5]
        H --> J[sharpen: 0.3]
        F --> K[saturation: 0.9]
        G --> L[contrast: 1.1]
    end
```

## History Apply Flow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant H as history.py
    participant S as settings.py
    participant A as audio.py

    B->>H: GET /history/{id}/apply
    H->>H: get_history_entry(id)
    H-->>H: HistoryEntry

    H->>S: update_category_preset(volume, entry.volume_preset)
    H->>S: update_category_preset(tunnel, entry.tunnel_preset)
    H->>S: update_category_preset(frequency, entry.frequency_preset)

    H->>A: _get_accordion_context()
    A-->>H: Full filter context

    H-->>B: filters_tabs.html
    Note right of B: HX-Trigger: historyApplied

    B->>B: Update clip range sliders
    B->>B: HTMX swap #filters-area
```

## Download Flow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant D as download.py
    participant DL as downloader.py
    participant YT as yt-dlp
    participant M as metadata.py

    B->>D: POST /download/validate
    D->>DL: validate_url()
    DL->>YT: yt-dlp --dump-json
    YT-->>DL: Video metadata
    DL-->>D: VideoInfo
    D-->>B: download_status.html (ready)

    B->>D: POST /download
    D->>DL: download_video()
    DL->>YT: yt-dlp -o output
    YT-->>DL: Downloaded file
    DL->>M: Store source metadata
    M-->>DL: {file}.yml created
    D-->>B: download_complete.html
```

## Error Handling States

```mermaid
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> Normal

    Normal --> ValidationError: Invalid input
    Normal --> ProcessingError: FFmpeg failure
    Normal --> NetworkError: Download failure
    Normal --> FileError: File not found

    ValidationError --> Normal: User corrects input
    ProcessingError --> Normal: Retry/different settings
    NetworkError --> Normal: Retry download
    FileError --> Normal: Re-upload file

    ProcessingError --> [*]: Unrecoverable
    NetworkError --> [*]: URL unavailable
```
