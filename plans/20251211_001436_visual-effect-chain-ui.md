# Visual Effect Chain UI

## Goal
Replace the current Effects column with a visual signal chain showing **Volume → Tunnel → Frequency** as connected boxes. Each category has its own presets. User settings persist to `.data/user_settings.yml`.

## UI Design
```
┌─────────────────────────────────────┐
│ EFFECT CHAIN                        │
│ ┌────────┐   ┌────────┐   ┌───────┐ │
│ │ 🔊     │ → │ 🏛️     │ → │ 📊    │ │
│ │ Volume │   │ Tunnel │   │ Freq  │ │
│ │  2x    │   │ Medium │   │ Flat  │ │
│ └────────┘   └────────┘   └───────┘ │
├─────────────────────────────────────┤
│ TUNNEL SETTINGS                     │
│ [None] [Subtle] [Medium] [Heavy]    │
│                                     │
│ Delays: [====●=====] 15|25|35|50    │
│ Decays: [====●=====] 0.35|0.3|...   │
└─────────────────────────────────────┘
```

## Category Presets

| Category | Presets |
|----------|---------|
| **Volume** | 1x, 1.5x, 2x, 3x, 4x |
| **Tunnel** | None, Subtle, Medium, Heavy, Extreme |
| **Frequency** | Flat, Bass Cut, Treble Cut, Narrow Band, Voice Clarity |

## Files to Modify

| File | Changes |
|------|---------|
| `app/models.py` | Add `VolumePreset`, `TunnelPreset`, `FrequencyPreset` enums + configs |
| `app/services/settings.py` | **NEW** - YAML load/save for user settings |
| `app/routers/audio.py` | Add `/partials/effect-chain`, `/partials/category-panel/{cat}`, `/partials/category-preset/{cat}/{preset}` |
| `app/templates/index.html` | Replace middle column with effect chain |
| `app/templates/partials/effect_chain.html` | **NEW** - Chain container |
| `app/templates/partials/effect_chain_boxes.html` | **NEW** - The 3 clickable boxes |
| `app/templates/partials/panel_volume.html` | **NEW** - Volume controls |
| `app/templates/partials/panel_tunnel.html` | **NEW** - Tunnel controls |
| `app/templates/partials/panel_frequency.html` | **NEW** - Frequency controls |
| `app/static/css/styles.css` | Add chain-box, chain-arrow, preset-pill, category-panel styles |

## User Settings Schema (`.data/user_settings.yml`)
```yaml
volume:
  preset: "2x"
  custom_values:
    volume: 2.0

tunnel:
  preset: "medium"
  custom_values:
    delays: "15|25|35|50"
    decays: "0.35|0.3|0.25|0.2"

frequency:
  preset: "flat"
  custom_values:
    highpass: 20
    lowpass: 20000

active_category: "volume"
```

## HTMX Flow
1. User clicks chain box → `hx-get="/partials/category-panel/{category}"` → panel updates
2. User clicks preset pill → `hx-post="/partials/category-preset/{cat}/{preset}"` → box badge updates + YAML saved
3. User adjusts slider → local JS updates value display (no HTMX until form submit)

## Implementation Phases

### Phase 1: Models & Settings Service
- [ ] Add category enums to `models.py` (VolumePreset, TunnelPreset, FrequencyPreset)
- [ ] Add category configs to `models.py` (VolumeConfig, TunnelConfig, FrequencyConfig)
- [ ] Add preset dictionaries (VOLUME_PRESETS, TUNNEL_PRESETS, FREQUENCY_PRESETS)
- [ ] Create `app/services/settings.py` with load/save functions

### Phase 2: Router Endpoints
- [ ] Add `GET /partials/effect-chain` endpoint
- [ ] Add `GET /partials/category-panel/{category}` endpoint
- [ ] Add `POST /partials/category-preset/{category}/{preset}` endpoint

### Phase 3: Templates
- [ ] Create `partials/effect_chain.html`
- [ ] Create `partials/effect_chain_boxes.html`
- [ ] Create `partials/panel_volume.html`
- [ ] Create `partials/panel_tunnel.html`
- [ ] Create `partials/panel_frequency.html`
- [ ] Update `index.html` middle column

### Phase 4: CSS
- [ ] Add `.effect-chain`, `.chain-container` styles
- [ ] Add `.chain-box`, `.chain-box.active` styles
- [ ] Add `.chain-arrow` styles
- [ ] Add `.preset-pills`, `.preset-pill` styles
- [ ] Add `.category-panel` styles
- [ ] Add responsive styles for mobile

### Phase 5: Integration
- [ ] Update `main.py` index route to load user settings
- [ ] Test HTMX interactions
- [ ] Verify YAML persistence
