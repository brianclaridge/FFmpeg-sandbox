# Layout, Effect Chain Bug, and UI Polish

## Issues to Address

### 1. Effect Chain Bug (CRITICAL)
Chain boxes appearing in Preview column instead of Effect Chain column.
- "Loading effect chain..." still visible = HTMX load not completing properly
- Chain boxes render in wrong location

**Root cause hypothesis:** HTMX `hx-trigger="load"` timing issue or target resolution problem.

**Fix:** Server-render effect chain on initial page load instead of HTMX lazy load.

### 2. Layout Improvements
- 10% viewport padding on left/right
- Minimum widths to prevent content wrapping
- Effect Chain (middle) gets bulk of space

### 3. Video Modal Polish
- Show "Loading..." centered until video is ready
- Position modal 100px from right/bottom edge (prevent scrollbars)

### 4. Footer Padding
- Add 50px bottom padding below footer (prevent scrollbars)

---

## Files to Modify

| File | Changes |
|------|---------|
| `app/templates/index.html` | Server-render effect chain (remove HTMX load) |
| `app/static/css/styles.css` | Layout grid, modal positioning, footer padding |

---

## Implementation

### Fix 1: Server-render Effect Chain

**index.html** - Replace HTMX load with server-side include:

```html
<!-- BEFORE (buggy) -->
<div id="effect-chain-area"
     hx-get="/partials/effect-chain"
     hx-trigger="load"
     hx-swap="innerHTML">
    <p class="placeholder">Loading effect chain...</p>
</div>

<!-- AFTER (server-rendered) -->
<div id="effect-chain-area">
    <div class="effect-chain">
        <div id="effect-chain-boxes">
            {% include "partials/effect_chain_boxes.html" %}
        </div>
    </div>
</div>
```

The template context already has all needed variables (`user_settings`, `volume_presets`, etc.).

### Fix 2: Layout CSS

```css
.container {
    max-width: none;
    padding: 2rem 10vw;
}

.grid-3 {
    grid-template-columns: minmax(280px, 1fr) minmax(400px, 2fr) minmax(280px, 1fr);
}

@media (max-width: 1200px) {
    .container { padding: 2rem 5vw; }
    .grid-3 { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 900px) {
    .container { padding: 1.5rem; }
    .grid-3 { grid-template-columns: 1fr; }
}
```

### Fix 3: Video Modal Positioning & Loading State

```css
.video-modal {
    bottom: 100px;  /* was 20px */
    right: 100px;   /* was 20px */
}
```

**index.html** - Add loading state:
```html
<div id="video-preview-modal" class="video-modal">
    <div class="video-modal-header">...</div>
    <div class="video-loading">Loading...</div>
    <video id="clip-preview-video" ...></video>
    ...
</div>
```

```css
.video-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: var(--text-secondary);
}
```

**JavaScript:** Hide loading text when video `canplay` event fires.

### Fix 4: Footer Bottom Padding

```css
footer {
    margin-bottom: 50px;
}
```

---

## Implementation Steps

- [ ] Server-render effect chain in index.html (remove HTMX load trigger)
- [ ] Update `.container` padding to `10vw` horizontal
- [ ] Update `.grid-3` with `minmax()` proportional columns
- [ ] Adjust responsive breakpoints
- [ ] Move video modal position (100px from edges)
- [ ] Add video loading state with centered "Loading..."
- [ ] Add footer bottom margin (50px)
- [ ] Test all changes
