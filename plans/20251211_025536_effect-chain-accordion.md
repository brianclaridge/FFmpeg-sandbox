# Effect Chain: Fix Preset Selection + Accordion Refactor

## Overview

Two issues with the effect chain UI:
1. **Bug**: Preset pills don't show as selected after clicking (panel doesn't re-render)
2. **Layout**: Horizontal chain doesn't scale for 4+ categories - refactor to accordion

---

## Problem Analysis

### Bug: Preset Selection Not Showing Active

**Current Flow:**
```
Click preset pill "Medium"
  → POST /partials/category-preset/volume/medium
  → Updates settings in file_metadata
  → Returns effect_chain_boxes.html
  → hx-target="#effect-chain-boxes" swaps ONLY the chain boxes
  → Panel still has OLD HTML with OLD active state
  → Pill doesn't get .active class
```

**Root Cause:** `hx-target="#effect-chain-boxes"` doesn't include the panel.

### Layout: Horizontal Chain Doesn't Scale

Current: `[Volume] → [Tunnel] → [Frequency]`
Problem: Adding 4th, 5th category makes horizontal layout unwieldy

---

## Proposed Solution: Accordion Layout

Replace horizontal chain boxes with a vertical accordion where:
- Each category is a collapsible section
- **Classic accordion**: expanding one section collapses others
- Preset pills and controls inside each accordion section
- Active preset shown in the header summary
- **Arrow indicators (↓)** between sections to show processing flow

```
┌─────────────────────────────────────┐
│ 🔊 Volume                    [2x] ▼ │
├─────────────────────────────────────┤
│   [1x] [1.5x] [2x•] [3x] [4x]      │
│   Volume: [====●====] 2.0          │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 🎙️ Tunnel                  [None] ▶ │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 📊 Frequency               [Flat] ▶ │
└─────────────────────────────────────┘
```

**Accordion Header Components:**
- Icon (emoji)
- Category name
- Current preset badge (right-aligned)
- Expand/collapse indicator (▼ expanded, ▶ collapsed)

---

## Files to Modify

| File | Changes |
|------|---------|
| `app/templates/partials/effect_chain.html` | New accordion container structure |
| `app/templates/partials/effect_chain_boxes.html` | Remove (merge into accordion) |
| `app/templates/partials/panel_*.html` | Integrate into accordion sections |
| `app/templates/index.html` | Update effect chain area structure |
| `app/routers/audio.py` | Update endpoints to return accordion sections |
| `app/static/css/styles.css` | Accordion styles, remove chain-box horizontal |

---

## Implementation Steps

### Phase 1: Create Accordion Structure
- [ ] Create `effect_chain_accordion.html` partial with accordion container
- [ ] Each section: header (clickable) + content (collapsible)
- [ ] Move panel content (preset pills + controls) into accordion sections
- [ ] Add ↓ arrows between sections

### Phase 2: HTMX Behavior
- [ ] Header click: `hx-get="/partials/accordion-section/{category}"`
- [ ] Swap entire accordion to collapse others, expand clicked
- [ ] Preset click: swap the accordion section to update active state
- [ ] Use `hx-target="#effect-chain-accordion"` for all swaps

### Phase 3: Update Endpoints
- [ ] New endpoint: `GET /partials/effect-chain-accordion` returns full accordion
- [ ] Update `set_category_preset` to return accordion (not just boxes)
- [ ] Update `get_category_panel` to set active and return accordion

### Phase 4: CSS Styling
- [ ] `.accordion-section` - collapsed/expanded states
- [ ] `.accordion-header` - clickable header with icon, name, preset, indicator
- [ ] `.accordion-content` - preset pills and controls
- [ ] `.accordion-arrow` - ↓ flow indicator between sections
- [ ] Smooth expand/collapse transitions
- [ ] Remove old `.chain-container`, `.chain-box`, `.chain-arrow` CSS

### Phase 5: Cleanup
- [ ] Remove `effect_chain_boxes.html` (merged into accordion)
- [ ] Remove separate `panel_*.html` files (content in accordion)
- [ ] Update `index.html` to use new accordion structure
- [ ] Test preset selection shows active state correctly
