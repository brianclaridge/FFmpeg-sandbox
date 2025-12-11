# Filename Anonymization, Per-File Metadata, and UI Polish

## Overview

Address long YouTube/Twitch filenames in dropdown, add per-file metadata with history, and polish UI elements.

---

## Changes

### 1. Filename Anonymization on Download

**Format:** `{source}-{id}.{ext}`
- YouTube: `yt-dQw4w9WgXcQ.mp4`
- Twitch: `tw-1234567890.mp4`
- Other: `dl-{hash8}.mp4`

**File:** `app/services/downloader.py`

```python
def get_source_prefix(extractor: str) -> str:
    """Map yt-dlp extractor to short prefix."""
    prefixes = {
        'youtube': 'yt',
        'twitch': 'tw',
        'vimeo': 'vm',
        'twitter': 'x',
        'tiktok': 'tt',
    }
    return prefixes.get(extractor.lower().split(':')[0], 'dl')

def sanitize_filename(title: str, video_id: str, extractor: str) -> str:
    """Create anonymized filename: {source}-{id}"""
    prefix = get_source_prefix(extractor)
    return f"{prefix}-{video_id}"
```

### 2. Per-File Metadata YAML (Replaces Global Settings)

Each input file gets a companion `.yml` with source metadata, processing history, AND effect chain settings.

**Location:** `.data/input/{slug}.yml` alongside `{slug}.mp4`

**Structure:**
```yaml
# yt-dQw4w9WgXcQ.yml
source:
  url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  title: "Rick Astley - Never Gonna Give You Up"
  uploader: "Rick Astley"
  duration: 212
  extractor: youtube
  downloaded_at: "2025-12-11T01:30:00Z"

settings:
  active_category: volume
  volume:
    preset: "2x"
    custom_values: {}
  tunnel:
    preset: "medium"
    custom_values: {}
  frequency:
    preset: "flat"
    custom_values: {}

history:
  - id: "abc123"
    output_file: "yt-dQw4w9WgXcQ_001.mp3"
    timestamp: "2025-12-11T01:35:00Z"
    params:
      start_time: "00:00:10.000"
      end_time: "00:00:25.000"
      volume: 2.0
      highpass: 100
      lowpass: 4500
```

**New Service:** `app/services/file_metadata.py`
- `load_file_metadata(filename) -> dict`
- `save_file_metadata(filename, metadata)`
- `add_history_entry(filename, entry)`
- `get_display_title(filename) -> str`
- `get_file_settings(filename) -> dict` (effect chain presets)
- `update_file_settings(filename, category, preset)`

**Migration:**
- Remove global `user_settings.yml`
- Remove `history.json`
- Refactor `app/services/settings.py` to use per-file metadata
- Settings loaded/saved per selected file

### 3. CSS Display Truncation (Fallback)

**Dropdown select truncation:**
```css
select#input_file {
    text-overflow: ellipsis;
    max-width: 100%;
}

select#input_file option {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

**Metadata filename word-wrap:**
```css
.metadata-filename {
    white-space: normal;      /* was: nowrap */
    word-wrap: break-word;
    overflow-wrap: break-word;
    /* Remove: overflow: hidden; text-overflow: ellipsis; */
}
```

### 4. Video Preview Button

Make square, use 🎥 icon, make bigger.

```css
.btn-video-preview {
    width: 56px;              /* was 52px */
    height: 56px;             /* explicit height for square */
    font-size: 1.75rem;       /* was 1.5rem */
    padding: 0;               /* was 1rem */
}
```

**HTML change:**
```html
<button type="button" id="clip-video-btn" class="btn-video-preview">
    <span>🎥</span>  <!-- was &#127902; (🎞️) -->
</button>
```

### 5. Video Modal Responsive Sizing

Prevent modal from overflowing viewport bounds.

```css
.video-modal {
    position: fixed;
    bottom: 100px;
    right: 100px;
    width: 640px;
    max-width: calc(100vw - 200px);   /* 100px margin each side */
    max-height: calc(100vh - 200px);  /* 100px margin top/bottom */
}

.video-modal video {
    max-width: 100%;
    max-height: calc(100vh - 300px);  /* account for header/footer */
    object-fit: contain;
}
```

### 6. Effect Chain Text Size

Increase label and preset text for better readability.

```css
.chain-box-icon {
    font-size: 1.5rem;        /* was 1.25rem */
}

.chain-box-label {
    font-size: 0.85rem;       /* was 0.7rem */
}

.chain-box-preset {
    font-size: 0.75rem;       /* was 0.6rem */
    padding: 0.15rem 0.5rem;  /* was 0.1rem 0.4rem */
}

.chain-box {
    min-width: 85px;          /* was 70px */
    padding: 1rem 0.75rem;    /* was 0.75rem 0.5rem */
}
```

### 7. Move Footer to Header Area

Move attribution from footer to right side of header, with link to .claude repo.

**Current (base.html):**
```html
<header>
    <h1>FFmpeg-sandbox</h1>
    ...
</header>
...
<footer>Built with FastAPI + HTMX</footer>
```

**New:**
```html
<header>
    <h1>FFmpeg-sandbox</h1>
    <span class="header-attribution">
        Built with FastAPI + HTMX + <a href="https://github.com/brianclaridge/.claude" target="_blank">.claude</a>
    </span>
    ...
</header>
<!-- Remove footer element -->
```

```css
.header-attribution {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-left: 100px;  /* offset from title */
}

.header-attribution a {
    color: var(--accent);
    text-decoration: none;
}

.header-attribution a:hover {
    text-decoration: underline;
}
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `app/services/downloader.py` | Anonymize filename format, create metadata YAML |
| `app/services/file_metadata.py` | **NEW** - Per-file YAML metadata service |
| `app/services/settings.py` | Refactor to use per-file metadata |
| `app/services/history.py` | Refactor to use file_metadata service |
| `app/routers/audio.py` | Update process endpoint, load settings per file |
| `app/routers/download.py` | Create metadata YAML on download |
| `app/main.py` | Update context to pass file-specific settings |
| `app/templates/index.html` | Video button icon, load settings on file select |
| `app/templates/base.html` | Move footer to header, add .claude link |
| `app/templates/partials/*.html` | Update to use file-specific context |
| `app/static/css/styles.css` | Truncation, button, modal sizing, effect chain, header attribution |
| `.data/user_settings.yml` | **DELETE** - replaced by per-file metadata |
| `.data/history.json` | **DELETE** - replaced by per-file metadata |

---

## Implementation Steps

### Phase 1: Core Infrastructure
- [ ] Create `app/services/file_metadata.py` with YAML read/write functions
- [ ] Update `downloader.py` to use `{source}-{id}` filename format
- [ ] Update `downloader.py` to create `.yml` metadata file on download

### Phase 2: Settings Migration
- [ ] Refactor `settings.py` to load/save per-file settings
- [ ] Update endpoints to pass current filename context
- [ ] Update effect chain to reload settings on file selection change

### Phase 3: History Migration
- [ ] Refactor `history.py` to store in per-file metadata YAML
- [ ] Update `audio.py` to use new history storage
- [ ] Update history display to filter by current file

### Phase 4: UI Polish
- [ ] Add CSS truncation for select dropdown
- [ ] Update `.metadata-filename` for word-wrap
- [ ] Update `.btn-video-preview` to square with 🎥 icon
- [ ] Add video modal responsive max-width/max-height
- [ ] Increase effect chain text sizes
- [ ] Move footer to header with .claude link

### Phase 5: Cleanup
- [ ] Remove deprecated `user_settings.yml` and `history.json`
- [ ] Test complete download → process → history flow
