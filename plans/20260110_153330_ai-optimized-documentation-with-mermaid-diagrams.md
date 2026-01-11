# Plan: AI-Optimized Documentation with Mermaid Diagrams

**Affects:** `/workspace/docs/ARCHITECTURE.md`, `/workspace/docs/API_REFERENCE.md`, `/workspace/docs/PROCESSING_FLOW.md`, `/workspace/docs/HTMX_PATTERNS.md`

---

## Objective

Create visual documentation optimized for agentic AI context acquisition:
- Dark-themed Mermaid diagrams (%%{init: {'theme': 'dark'}}%%)
- C4 model architecture layers
- Sequence diagrams for request flows
- State diagrams for UI components
- ER diagram for data models
- Decision flowcharts

---

## File 1: docs/ARCHITECTURE.md

### Content Structure

1. **C4 Context Diagram** - System boundary with external actors
2. **C4 Container Diagram** - FastAPI, FFmpeg, File System
3. **Component Diagram** - Service layer modules
4. **Module Dependency Graph** - Import relationships

### Mermaid Diagrams

```markdown
## C4 Context
%%{init: {'theme': 'dark'}}%%
graph TB
    User[User Browser] --> App[FFmpeg Sandbox]
    App --> FFmpeg[FFmpeg CLI]
    App --> YtDlp[yt-dlp]
    App --> FileSystem[.data/ Storage]

## Component Diagram
%%{init: {'theme': 'dark'}}%%
graph LR
    subgraph Routers
        audio.py --> processor.py
        download.py --> downloader.py
        history.py --> history_svc[history.py service]
    end
    subgraph Services
        processor.py --> filter_chain.py
        filter_chain.py --> filters_audio.py
        filter_chain.py --> filters_video.py
        processor.py --> ffmpeg_executor.py
    end
```

---

## File 2: docs/API_REFERENCE.md

### Content Structure

1. **Endpoint Summary Table** - All 28 endpoints at a glance
2. **Grouped by Router** - audio, download, history
3. **Each Endpoint Section:**
   - Method + Path
   - Parameters (path, query, form)
   - Response type + template
   - HTMX trigger location
   - Example request/response

### Format

```markdown
## POST /process

**Router:** `audio.py:148`

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| input_file | str | Yes | - |
| start_time | str | No | 00:00:00.000 |
| end_time | str | No | 00:00:06.000 |
| output_format | str | No | mp4 |

**Response:** `partials/preview.html`

**HTMX Trigger:** `index.html:4`
```html
<form hx-post="/process" hx-target="#preview-area">
```
```

---

## File 3: docs/PROCESSING_FLOW.md

### Content Structure

1. **Upload → Process Sequence Diagram**
2. **Filter Chain Building Flowchart**
3. **SSE Progress Streaming Sequence**
4. **Theme Preset Application Flow**

### Mermaid Diagrams

```markdown
## Processing Sequence
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant B as Browser
    participant F as FastAPI
    participant S as Services
    participant FF as FFmpeg

    B->>F: POST /process
    F->>S: load_user_settings()
    F->>S: build_filter_chain()
    S->>FF: ffmpeg -i input -af/-vf filters output
    FF-->>S: completion
    S->>F: add_history_entry()
    F-->>B: preview.html

## SSE Progress Flow
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    B->>F: GET /process-with-progress (SSE)
    loop Every 100ms
        F-->>B: event: progress {percent, current_ms}
    end
    F-->>B: event: complete {output_file}
    B->>B: Close modal, refresh history
```

---

## File 4: docs/HTMX_PATTERNS.md

### Content Structure

1. **Swap Strategy Reference**
2. **Template → Endpoint Mapping Table**
3. **Custom Events (HX-Trigger headers)**
4. **Dynamic Value Patterns (hx-vals)**

### Mermaid Diagrams

```markdown
## HTMX Request Flow
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A[User Click] --> B{HTMX Attribute}
    B -->|hx-get| C[GET Request]
    B -->|hx-post| D[POST Request]
    B -->|hx-delete| E[DELETE Request]
    C --> F[Server Response]
    D --> F
    E --> F
    F --> G{hx-swap}
    G -->|innerHTML| H[Replace Children]
    G -->|outerHTML| I[Replace Element]

## Accordion State Machine
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> Collapsed
    Collapsed --> Expanded: Click header
    Expanded --> Collapsed: Click different header
    Expanded --> PresetApplied: Click shortcut pill
    PresetApplied --> Expanded: Animation complete
```

---

## Additional Diagrams (Distributed Across Files)

### State Diagram (PROCESSING_FLOW.md)

```markdown
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> Idle
    Idle --> Uploading: Select file
    Uploading --> Ready: Upload complete
    Ready --> Processing: Click Process
    Processing --> Complete: FFmpeg success
    Processing --> Error: FFmpeg failure
    Complete --> Ready: Process another
    Error --> Ready: Retry
```

### ER Diagram (ARCHITECTURE.md)

```markdown
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
        string id
        datetime timestamp
        string input_file
        string output_file
        string start_time
        string end_time
    }
    ThemePreset ||--|{ FilterStep : contains
    ThemePreset {
        string name
        string description
        string icon
    }
    FilterStep {
        string type
        dict params
    }
```

### Filter Chain Flowchart (PROCESSING_FLOW.md)

```markdown
%%{init: {'theme': 'dark'}}%%
flowchart TD
    A[Start] --> B{Audio or Video?}
    B -->|Audio| C[Build Audio Chain]
    B -->|Video| D[Build Video Chain]

    C --> C1[Volume Filter]
    C1 --> C2[Frequency Filter]
    C2 --> C3[Tunnel/Echo]
    C3 --> C4[Speed]
    C4 --> C5[Pitch]
    C5 --> C6[Noise Reduction]
    C6 --> C7[Compressor]
    C7 --> E[Combine Filters]

    D --> D1[Crop]
    D1 --> D2[Scale]
    D2 --> D3[Colorshift]
    D3 --> D4[EQ]
    D4 --> D5[Blur]
    D5 --> D6[Sharpen]
    D6 --> D7[Transform]
    D7 --> D8[Speed]
    D8 --> D9[Overlay]
    D9 --> E

    E --> F[FFmpeg Command]
```

---

## Implementation Order

1. Create `docs/ARCHITECTURE.md` with C4 + ER diagrams
2. Create `docs/API_REFERENCE.md` with all 28 endpoints
3. Create `docs/PROCESSING_FLOW.md` with sequence + state diagrams
4. Create `docs/HTMX_PATTERNS.md` with swap patterns + flowcharts
5. Update `docs/ROADMAP.md` to mark documentation phase complete

---

## Verification

1. All Mermaid diagrams render correctly on GitHub
2. Dark theme applied to all diagrams
3. Cross-references between docs work
4. API reference covers all 28 endpoints
5. Diagrams accurately reflect current codebase
