# Plan: Refactor processor.py into 6 Modules

## Task
Split `app/services/processor.py` (669 lines, 19 functions) into 6 focused modules without losing functionality.

## Target Structure

```
app/services/
├── __init__.py           (update exports)
├── processor.py          (~260 lines) - Processing orchestration
├── metadata.py           (~119 lines) - File introspection
├── filters_audio.py      (~82 lines)  - Audio effect builders
├── filters_video.py      (~40 lines)  - Video effect builders
├── filter_chain.py       (~104 lines) - Filter aggregation
└── ffmpeg_executor.py    (~60 lines)  - Subprocess management
```

## Module Contents

### 1. `metadata.py` (119 lines)
```python
# Functions to move:
- get_file_duration()
- get_file_metadata()
- get_input_files()
- format_duration_ms()
- format_file_size()
- format_bitrate()
```

### 2. `filters_audio.py` (82 lines)
```python
# Functions to move:
- build_speed_filter()
- build_pitch_filter()
- build_noise_reduction_filter()
- build_compressor_filter()
```

### 3. `filters_video.py` (40 lines)
```python
# Functions to move:
- build_eq_filter()
- build_blur_filter()
- build_sharpen_filter()
- build_transform_filter()
```

### 4. `filter_chain.py` (104 lines)
```python
# Functions to move:
- build_audio_filter_chain()  # imports from filters_audio
- build_video_filter_chain()  # imports from filters_video
```

### 5. `ffmpeg_executor.py` (~60 lines)
```python
# New module - extract common subprocess logic:
- run_ffmpeg_command()  # wrapper for subprocess calls
- FFmpegError exception class
```

### 6. `processor.py` (~260 lines)
```python
# Remaining functions:
- process_audio()              # refactor to use build_audio_filter_chain()
- process_audio_with_effects()
- process_video_with_effects()
```

## Files to Update (Imports)

| File | Changes |
|------|---------|
| `app/routers/audio.py` | Update imports for metadata, filter_chain functions |
| `app/main.py` | Update imports if needed |
| `app/services/__init__.py` | Re-export all public functions |

## Execution Order

1. Create `metadata.py` - no dependencies, move formatters first
2. Create `filters_audio.py` - pure functions, no deps
3. Create `filters_video.py` - pure functions, no deps
4. Create `filter_chain.py` - imports from filters_audio/video
5. Create `ffmpeg_executor.py` - extract subprocess wrapper
6. Refactor `processor.py` - imports from all new modules
7. Update `__init__.py` - re-export public API
8. Update router imports - `audio.py`, `main.py`
9. Rebuild and test

## TODO
- [ ] Create metadata.py with file introspection functions
- [ ] Create filters_audio.py with audio filter builders
- [ ] Create filters_video.py with video filter builders
- [ ] Create filter_chain.py with chain aggregators
- [ ] Create ffmpeg_executor.py with subprocess wrapper
- [ ] Refactor processor.py to import from new modules
- [ ] Fix process_audio() duplication by using build_audio_filter_chain()
- [ ] Update services/__init__.py exports
- [ ] Update imports in routers/audio.py
- [ ] Update imports in main.py if needed
- [ ] Rebuild and test container
