# Plan: UI Enhancements - Format Dropdown Position & Video Player Theming

**Date:** 2025-12-13
**Status:** Ready for approval

## Objectives

1. Move Format dropdown to the right of the Process button
2. Video player controls match page theme (use CSS variables)
3. Replace Unicode icons with Font Awesome icons

## Files to Modify

| File | Changes |
|------|---------|
| `app/templates/index.html` | Reorder format/button elements, replace video control icons |
| `app/static/css/media.css` | Update video controls to use theme variables |

---

## Task 1: Move Format Dropdown

**File:** `app/templates/index.html` (lines 126-146)

**Current order:**
```html
<div class="process-row filter-chain-process">
    <div class="format-selection">...</div>  <!-- LEFT -->
    <button class="btn-primary">...</button>  <!-- RIGHT -->
</div>
```

**New order:**
```html
<div class="process-row filter-chain-process">
    <button class="btn-primary">...</button>  <!-- LEFT -->
    <div class="format-selection">...</div>  <!-- RIGHT -->
</div>
```

**CSS Impact:** None - flexbox `justify-content: space-between` handles positioning

---

## Task 2: Video Player Theme Integration

**File:** `app/static/css/media.css` (lines 143-187)

### 2.1 Update `.video-controls` container

**Before:**
```css
.video-controls {
    background: white;
    /* ... */
}
```

**After:**
```css
.video-controls {
    background: var(--bg-secondary);
    /* ... */
}
```

### 2.2 Update `.video-ctrl-btn` styling

**Before:**
```css
.video-ctrl-btn {
    background: transparent;
    border: 1px solid #ccc;
    color: #333;
    /* ... */
}
```

**After:**
```css
.video-ctrl-btn {
    background: transparent;
    border: 1px solid var(--slider-border);
    color: var(--text-primary);
    /* ... */
}
```

### 2.3 Update `.loop-btn.active` styling

**Before:**
```css
.loop-btn.active {
    background: #333;
    color: white;
    border-color: #333;
}
```

**After:**
```css
.loop-btn.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}
```

---

## Task 3: Font Awesome Icons

**File:** `app/templates/index.html` (lines 176-187)

Font Awesome 6.5.1 is already loaded via CDN.

### 3.1 Replace video control button content

| Button | Current (Unicode) | New (Font Awesome) |
|--------|-------------------|-------------------|
| Play | `<span class="play-icon">▶</span>` | `<i class="fa-solid fa-play play-icon"></i>` |
| Pause | `<span class="pause-icon">⏸⏸</span>` | `<i class="fa-solid fa-pause pause-icon"></i>` |
| Stop | `■` | `<i class="fa-solid fa-stop"></i>` |
| Loop | `∞` | `<i class="fa-solid fa-repeat"></i>` |

### 3.2 Updated HTML structure

```html
<div class="video-controls">
    <button type="button" id="video-play-btn" class="video-ctrl-btn" title="Play/Pause">
        <i class="fa-solid fa-play play-icon"></i>
        <i class="fa-solid fa-pause pause-icon" style="display:none;"></i>
    </button>
    <button type="button" id="video-stop-btn" class="video-ctrl-btn" title="Stop">
        <i class="fa-solid fa-stop"></i>
    </button>
    <button type="button" id="video-loop-btn" class="video-ctrl-btn loop-btn active" title="Toggle Loop">
        <i class="fa-solid fa-repeat"></i>
    </button>
</div>
```

### 3.3 JavaScript compatibility

The existing JavaScript uses `.querySelector('.play-icon')` and `.querySelector('.pause-icon')` - these selectors work with both `<span>` and `<i>` elements as long as the class names are preserved.

No JavaScript changes required.

---

## Implementation Checklist

- [ ] Reorder format dropdown and process button in index.html
- [ ] Update .video-controls background in media.css
- [ ] Update .video-ctrl-btn colors in media.css
- [ ] Update .loop-btn.active colors in media.css
- [ ] Replace Unicode icons with Font Awesome in index.html
- [ ] Test all 10 themes for visual consistency
- [ ] Verify play/pause toggle still works

## Success Criteria

1. Format dropdown appears to the right of Process button
2. Video controls match current theme (no white background on dark themes)
3. Font Awesome icons display correctly
4. Play/pause toggle functionality preserved
5. Loop button active state uses accent color
