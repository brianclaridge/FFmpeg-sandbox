# URL Video Download Feature

Add ability to download videos from URLs (YouTube, Twitch, Twitter, TikTok, 1000+ sites) using yt-dlp, save to `data/input/`, and process as audio.

## User Selections
- **Download tool**: yt-dlp (Python library)
- **Platform scope**: Any yt-dlp supported URL
- **File retention**: Move to input folder (permanent)
- **UI approach**: Separate URL section below file selector

## Files to Modify/Create

| File | Action |
|------|--------|
| `pyproject.toml` | Add yt-dlp dependency |
| `app/services/downloader.py` | NEW: Download service |
| `app/routers/download.py` | NEW: /download endpoints |
| `app/main.py` | Register download router |
| `app/templates/index.html` | Add URL input section |
| `app/templates/partials/download_status.html` | NEW: Status partial |
| `app/templates/partials/download_complete.html` | NEW: Success partial |
| `app/static/css/styles.css` | Add URL section styles |
| `Dockerfile` | Add yt-dlp system dependency |

## Implementation Steps

### 1. Add Dependency
```toml
# pyproject.toml
"yt-dlp>=2024.1.0",
```

### 2. Create Download Service (`app/services/downloader.py`)
- `validate_url(url)` - Check URL format and yt-dlp support
- `get_video_info(url)` - Fetch metadata without downloading
- `download_video(url)` - Download to INPUT_DIR
- `sanitize_filename(title, id)` - Safe filename with video ID suffix

### 3. Create Download Router (`app/routers/download.py`)
| Endpoint | Description |
|----------|-------------|
| `POST /download/validate` | Validate URL, return video info preview |
| `POST /download` | Execute download, update file selector |

### 4. Update Main App
```python
from app.routers import audio, history, download
app.include_router(download.router)
```

### 5. Template Changes

**index.html** - Add after file selector:
```html
<div class="url-section">
  <div class="section-divider"><span>or download from URL</span></div>
  <div class="url-input-group">
    <input type="text" id="download_url" placeholder="Paste video URL...">
    <button hx-post="/download/validate" hx-target="#download-status">Check URL</button>
  </div>
  <div id="download-status"></div>
</div>
```

**partials/download_status.html** - Shows:
- Error state with message
- Ready state with video info + Download button
- Downloading state with progress

**partials/download_complete.html** - Shows:
- Success message
- OOB swap to update file selector with new file selected

### 6. CSS Updates
- `.url-section` - Container styling
- `.section-divider` - "or download from URL" separator
- `.url-input-group` - Input + button flex row
- `.download-preview` - Video info card
- `.download-error/.download-success` - Status states

### 7. Update Dockerfile
```dockerfile
RUN apt-get install -y --no-install-recommends ffmpeg && \
    pip install yt-dlp
```

## User Flow
```
1. Paste URL → Click "Check URL"
2. See video title, duration, source
3. Click "Download" → Progress indicator
4. Success → File auto-selected in dropdown
5. Configure effects → Process
```

## Error Handling
- Invalid URL format → Immediate feedback
- Unsupported site → Helpful error message
- Video not found/private → Clear explanation
- Network failure → Retry suggestion
- Download in progress → Disable button

## TODO List
1. [ ] Add yt-dlp to pyproject.toml
2. [ ] Create app/services/downloader.py
3. [ ] Create app/routers/download.py
4. [ ] Register router in app/main.py
5. [ ] Add URL section to index.html
6. [ ] Create partials/download_status.html
7. [ ] Create partials/download_complete.html
8. [ ] Add CSS styles for URL section
9. [ ] Update Dockerfile for yt-dlp
10. [ ] Update Taskfile.yml with download tasks
11. [ ] Test with YouTube, Twitch, Twitter URLs
