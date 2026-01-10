# Filters Reference

FFmpeg Sandbox supports 13 filter categories across audio and video processing.

## Audio Filters (7)

| Filter | Description | Range |
|--------|-------------|-------|
| **Volume** | Amplitude adjustment | 0.0 - 3.0 |
| **Tunnel** | Reverb/echo effect | 0 - 100 |
| **Frequency** | EQ / frequency shaping | Preset-based |
| **Speed** | Playback speed | 0.5x - 4.0x |
| **Pitch** | Pitch shift | -12 to +12 semitones |
| **Noise Reduction** | Background noise removal | 0 - 100 |
| **Compressor** | Dynamic range compression | Preset-based |

## Video Filters (6)

| Filter | Description | Range |
|--------|-------------|-------|
| **Brightness** | Light level adjustment | -1.0 to 1.0 |
| **Contrast** | Tonal range | 0.0 - 3.0 |
| **Saturation** | Color intensity | 0.0 - 3.0 |
| **Blur** | Gaussian blur | 0 - 20 sigma |
| **Sharpen** | Edge enhancement | 0 - 5.0 |
| **Transform** | Flip, rotate, crop | Preset-based |

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
