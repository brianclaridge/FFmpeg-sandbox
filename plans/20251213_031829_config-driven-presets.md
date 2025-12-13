# Plan: Config-Driven Effect Presets

## Objective
Evaluate whether to move audio/video effect presets from `models.py` to `config.yml` for easier customization without code changes.

## Current State Analysis

### Preset Categories (14 total)
| Category | Type | Presets | Config Class |
|----------|------|---------|--------------|
| PresetLevel | Legacy | 5 | PresetConfig |
| Volume | Audio | 8 | VolumeConfig |
| Tunnel | Audio | 5 | TunnelConfig |
| Frequency | Audio | 6 | FrequencyConfig |
| Speed | Audio | 7 | SpeedConfig |
| Pitch | Audio | 7 | PitchConfig |
| NoiseReduction | Audio | 4 | NoiseReductionConfig |
| Compressor | Audio | 4 | CompressorConfig |
| Brightness | Video | 5 | BrightnessConfig |
| Contrast | Video | 5 | ContrastConfig |
| Saturation | Video | 5 | SaturationConfig |
| Blur | Video | 4 | BlurConfig |
| Sharpen | Video | 4 | SharpenConfig |
| Transform | Video | 6 | TransformConfig |

**Total: ~75 preset definitions across 14 categories**

### Current Architecture
```
models.py (750+ lines)
├── Enum classes (VolumePreset, TunnelPreset, etc.)
├── Config classes (VolumeConfig, TunnelConfig, etc.)
├── Preset dictionaries (VOLUME_PRESETS, TUNNEL_PRESETS, etc.)
└── *_BY_STR lookup dictionaries
```

## Options

### Option A: Keep in models.py (Current)
**Pros:**
- Type-safe with Pydantic validation
- IDE autocompletion and refactoring support
- Compile-time error detection
- Fast runtime (no file I/O)

**Cons:**
- Requires code change + Docker rebuild for new presets
- Non-developers cannot easily customize
- ~250 lines of boilerplate per category

**Effort:** None (status quo)

---

### Option B: Full Migration to config.yml
**Pros:**
- Hot-reloadable presets (no rebuild)
- YAML is user-friendly
- Single source of truth
- Easier to add/modify presets

**Cons:**
- Loses Pydantic type safety
- No IDE support for preset definitions
- Runtime validation required
- Migration effort for 75+ presets
- Potential YAML parsing errors

**Implementation:**
```yaml
# config.yml
presets:
  audio:
    volume:
      - key: "none"
        name: "None"
        description: "No effect (original)"
        volume: 1.0
      - key: "2x"
        name: "2x"
        description: "Double volume"
        volume: 2.0
    tunnel:
      - key: "none"
        name: "None"
        delays: [1]
        decays: [0.0]
```

**Effort:** High (2-3 phases)

---

### Option C: Hybrid Approach
Keep default presets in code, allow config.yml overrides.

**Pros:**
- Sensible defaults out of box
- Users can customize without touching code
- Type-safe defaults
- Additive customization

**Cons:**
- More complex merging logic
- Two places to look for presets
- Harder to reason about final state

**Implementation:**
```python
# Load defaults from code, merge with config
presets = merge(VOLUME_PRESETS, config.get("presets.volume", {}))
```

**Effort:** Medium

---

### Option D: External Presets File (presets.yml)
Separate presets into dedicated YAML file, keep models.py for schemas only.

**Pros:**
- Clean separation of concerns
- models.py stays small (schema only)
- presets.yml is focused and readable
- Can validate YAML against Pydantic schema

**Cons:**
- Additional file to maintain
- Still requires validation code

**Effort:** Medium

## Recommendation

**Option D (External Presets File)** offers the best balance:
1. Keep Pydantic Config classes in models.py as schema
2. Move preset values to `presets.yml`
3. Load and validate on startup
4. Hot-reload capability possible with file watcher

## Implementation Phases (if approved)

### Phase 1: Schema Refactor
- [ ] Extract preset schema classes to `models/presets.py`
- [ ] Create `presets.yml` with current preset values
- [ ] Implement loader with Pydantic validation
- [ ] Update `main.py` to load presets on startup

### Phase 2: Template Updates
- [ ] Update templates to use loaded presets
- [ ] Ensure backwards compatibility
- [ ] Test all 14 categories

### Phase 3: Hot Reload (Optional)
- [ ] Add file watcher for `presets.yml`
- [ ] Implement reload without restart
- [ ] Add admin endpoint to trigger reload

## Questions for User
1. Do you want hot-reload capability?
2. Should custom presets merge with or replace defaults?
3. Priority: Quick wins (Phase 1) or full implementation?

## Risks
- YAML syntax errors could break startup
- Migration of 75+ presets needs careful testing
- Templates reference preset dictionaries directly

---

## User Decisions
- **Selected Approach:** Option D (External presets.yml file)
- **Hot Reload:** Not required (restart acceptable)

## Revised Implementation Plan

### Phase 1: Create presets.yml and Loader
- [x] Create `presets.yml` with all current preset values
- [x] Create `app/services/presets.py` loader with Pydantic validation
- [x] Update `main.py` to load presets on startup
- [x] Verify presets load correctly

### Phase 2: Template Integration
- [x] Update template context to use loaded presets
- [x] Update `routers/audio.py` to use new presets loader
- [x] Update `routers/history.py` to use new presets loader
- [x] Ensure preset pills and sliders work correctly

### Phase 3: Cleanup
- [ ] Remove hardcoded presets from `models.py` (keep schemas) - DEFERRED
- [x] Update imports across codebase
- [x] Rebuild and full test

---

**Status:** Implemented
**Created:** 2025-12-13
**Completed:** 2025-12-13
