# Common Tasks

How-to guides for common development operations.

## Add a New Shortcut

Edit `presets.yml`:

```yaml
audio:
  volume:
    new_preset:
      name: "New Preset"
      description: "Description here"
      volume: 1.5
```

Run `task rebuild` to restart container. Presets are validated on startup via `app/services/presets.py`.

## Add a New Theme Preset

Edit `presets_themes.yml`:

```yaml
video:
  new_theme:
    name: "New Theme"
    description: "Theme description"
    icon: "fa-star"
    filters:
      - type: saturation
        params:
          saturation: 1.5
      - type: contrast
        params:
          contrast: 1.2
```

Run `task rebuild` to restart container.

## Add a New CSS Theme

Add to `app/static/css/themes.css`:

```css
[data-theme="newtheme"] {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --text-primary: #eee;
    --accent: #e94560;
    /* ... other CSS variables */
}
```

Add option to `templates/base.html` theme selector dropdown.

## Modify Filter Chain

- **Chain logic**: Edit `app/services/filter_chain.py`
- **Audio filters**: Edit `app/services/filters_audio.py`
- **Video filters**: Edit `app/services/filters_video.py`

## Add a New Filter Category

1. Add Pydantic schema to `app/models.py`
2. Add filter builder to `filters_audio.py` or `filters_video.py`
3. Add to chain in `filter_chain.py`
4. Add presets to `presets.yml`
5. Add UI accordion section to templates

## Add a New API Endpoint

1. Create or edit router in `app/routers/`
2. Include router in `app/main.py`
3. Add template partial if needed

## Debug FFmpeg Commands

Check the generated FFmpeg command in container logs:

```bash
docker logs workspace-ffmpeg-sandbox-1 2>&1 | grep -A5 "FFmpeg command"
```

Or view logs in `.data/logs/`.
