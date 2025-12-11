# Compact Header + History Play Fix

## Goals
1. Reduce vertical space in header - single line with title left, theme right
2. Fix history Play button to play inline instead of downloading

## Changes

### 1. `app/templates/base.html`
- Change title to "Audio Hacker"
- Remove subtitle paragraph
- Use flexbox: title left, theme dropdown right on one line

### 2. `app/static/css/styles.css`
- Update `.container > header` to flexbox with space-between, align-items center
- Remove h1 centering, reduce margin-bottom
- Style for inline audio player in history items

### 3. `app/templates/partials/history.html`
- Replace `<a href="/preview/...">Play</a>` link with inline audio element
- Or add click handler that plays audio without navigation

## Files
- `app/templates/base.html`
- `app/static/css/styles.css`
- `app/templates/partials/history.html`
