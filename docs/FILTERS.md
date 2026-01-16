# Filters Reference

FFmpeg Sandbox supports 13 filter categories across audio and video processing.

## Audio Filters (7)

| Category | Presets | Description |
|----------|---------|-------------|
| **Volume** | None, 0.25x-4x | Gain control (mute to 4x boost) |
| **Tunnel** | None, Subtle, Medium, Heavy, Extreme | Echo/reverb effects |
| **Frequency** | Flat, Bass Cut, Treble Cut, Narrow, Voice | High/low-pass filtering |
| **Speed** | 0.5x-2x | Playback speed adjustment |
| **Pitch** | Low, Normal, High, Chipmunk | Pitch shifting (semitones) |
| **Noise Reduction** | None, Light, Medium, Heavy | Background noise removal |
| **Compressor** | None, Light, Podcast, Broadcast | Dynamic range control |

### Audio Filter Ranges

| Filter | Range | Notes |
|--------|-------|-------|
| Volume | 0.0 - 3.0 | Amplitude multiplier |
| Tunnel | 0 - 100 | Echo intensity |
| Frequency | Preset-based | High/low-pass combinations |
| Speed | 0.5x - 4.0x | Playback rate |
| Pitch | -12 to +12 semitones | Pitch shift |
| Noise Reduction | 0 - 100 | Reduction strength |
| Compressor | Preset-based | Threshold/ratio combinations |

## Video Filters (6)

| Category | Presets | Description |
|----------|---------|-------------|
| **Brightness** | Dark, Normal, Bright | Image brightness |
| **Contrast** | Low, Normal, High | Image contrast |
| **Saturation** | Grayscale, Muted, Normal, Vivid | Color saturation |
| **Blur** | None, Light, Medium, Heavy | Gaussian blur |
| **Sharpen** | None, Light, Medium, Strong | Edge enhancement |
| **Transform** | Flip H/V, Rotate 90/180/270 | Geometric transforms |

### Video Filter Ranges

| Filter | Range | Notes |
|--------|-------|-------|
| Brightness | -1.0 to 1.0 | Light level |
| Contrast | 0.0 - 3.0 | Tonal range |
| Saturation | 0.0 - 3.0 | Color intensity |
| Blur | 0 - 20 sigma | Gaussian blur |
| Sharpen | 0 - 5.0 | Edge enhancement |
| Transform | Preset-based | Flip, rotate operations |

## Shortcuts (presets.yml)

66 filter shortcuts across 13 categories. Each shortcut sets optimal slider values for common use cases.

**Example:**
```yaml
audio:
  volume:
    whisper:
      name: "Whisper"
      description: "Very quiet output"
      volume: 0.3
```

## Theme Presets (presets_themes.yml)

Multi-filter transformation pipelines that apply several effects at once.

### Video Themes

| Preset | Description | Filters Applied |
|--------|-------------|-----------------|
| **CRT Playback** | 240p 4:3 for CRT television | crop, scale, blur |
| **VHS Playback** | 4:3 retro VHS look | crop, saturation, contrast, blur |
| **Film Grain** | Cinematic film look | contrast, saturation, sharpen |
| **Silent Film** | Black and white silent movie | saturation (0), contrast |
| **Security Cam** | CCTV overlay with timestamp | overlay, contrast |
| **Glitch Art** | Digital corruption effect | colorshift, blur |
| **Night Vision** | Green-tinted night look | saturation, brightness |

### Audio Themes

| Preset | Description | Filters Applied |
|--------|-------------|-----------------|
| **Vinyl Record** | Warm analog vinyl sound | frequency, noise |
| **Old Radio** | AM radio broadcast | frequency, compression |
| **Telephone** | Phone call quality | frequency, volume |
| **Cassette Tape** | Tape deck warmth | frequency, noise, saturation |
| **Podcast Ready** | Voice optimization | compression, frequency, noise |
| **Underwater** | Muffled underwater effect | frequency, reverb |

## Configuration Files

| File | Purpose |
|------|---------|
| `presets.yml` | 66 filter shortcuts (slider values) |
| `presets_themes.yml` | 12 themed transformation pipelines |
| `app/services/presets.py` | Shortcut loader with Pydantic validation |
| `app/services/presets_themes.py` | Theme preset loader |
