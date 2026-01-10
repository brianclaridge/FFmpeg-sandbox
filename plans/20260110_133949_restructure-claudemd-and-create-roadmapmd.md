# Plan: Restructure CLAUDE.md and Create ROADMAP.md

**Affects:** `/workspace/CLAUDE.md`, `/workspace/docs/`, `/workspace/ROADMAP.md`

---

## Objective

1. Create comprehensive ROADMAP.md with current + new feature ideas, ordered by priority
2. Break CLAUDE.md (212 lines) into topic-based `./docs/*.md` files
3. Keep CLAUDE.md terse (~50 lines) as table of contents for Claude Code
4. Follow Claude Code documentation best practices

---

## New File Structure

```
/workspace/
├── CLAUDE.md              # Terse TOC (~50 lines)
├── ROADMAP.md             # Development roadmap (linked from CLAUDE.md)
└── docs/
    ├── PROJECT_STRUCTURE.md   # Directory tree + descriptions
    ├── FILTERS.md             # Filter categories + presets reference
    └── COMMON_TASKS.md        # How-to guides
```

---

## Step 1: Create docs/ Directory

```bash
mkdir -p /workspace/docs
```

---

## Step 2: Create ROADMAP.md

**Location:** `/workspace/ROADMAP.md` (root level for visibility)

**Content:**
- Priority-ordered phases (High → Low)
- New feature ideas beyond current roadmap
- Completed phases (collapsed)
- Technical debt tracking

**Proposed Structure:**

```markdown
# Development Roadmap

## High Priority
- Phase: Output Format Options (MP3/WAV/FLAC, MP4/WebM, quality selection)
- Phase: Batch Processing (multi-file, ZIP export)

## Medium Priority
- Phase: Audio Filter QA (validate interactions)
- Phase: Waveform Visualization
- Phase: Preset Sharing (export/import themed presets)

## Future Ideas
- Real-time preview with filter chain
- Audio normalization presets
- Video stabilization filter
- Subtitle overlay support
- Custom FFmpeg command builder
- Preset marketplace/community sharing
- API mode for programmatic access
- WebSocket live progress
- Undo/redo for filter changes

## Completed Phases
(collapsed sections for history)

## Technical Debt
(resolved items tracked here)
```

---

## Step 3: Create docs/PROJECT_STRUCTURE.md

Move lines 23-97 from CLAUDE.md (project structure tree with annotations).

---

## Step 4: Create docs/FILTERS.md

**Content:**
- Audio filters (7): Volume, Tunnel, Frequency, Speed, Pitch, Noise Reduction, Compressor
- Video filters (6): Brightness, Contrast, Saturation, Blur, Sharpen, Transform
- Reference to presets.yml and presets_themes.yml
- Theme presets list (VHS, Vinyl, etc.)

---

## Step 5: Create docs/COMMON_TASKS.md

Move lines 115-147 from CLAUDE.md:
- Add a new preset
- Add a new theme
- Modify filter chain

---

## Step 6: Rewrite CLAUDE.md as TOC

**Target:** ~50 lines, scannable format

```markdown
# FFmpeg Sandbox

Audio/video processing app with 13 filter categories and YAML-driven presets.

## Quick Start

\`\`\`bash
task rebuild     # After every change
uv sync          # Install deps
docker compose up -d
\`\`\`

## Tech Stack

FastAPI | HTMX | Jinja2 | FFmpeg | yt-dlp | uv

## Documentation

| Doc | Description |
|-----|-------------|
| [ROADMAP.md](ROADMAP.md) | Development phases and priorities |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Directory tree and file purposes |
| [docs/FILTERS.md](docs/FILTERS.md) | Audio/video filter categories |
| [docs/COMMON_TASKS.md](docs/COMMON_TASKS.md) | How-to guides |

## Key Files

| File | Purpose |
|------|---------|
| `presets.yml` | 66 filter shortcuts across 13 categories |
| `presets_themes.yml` | 12 themed transformation presets |
| `config.yml` | Application configuration |
```

---

## Implementation Order

1. Create `docs/` directory
2. Create `docs/PROJECT_STRUCTURE.md` (extract from CLAUDE.md)
3. Create `docs/FILTERS.md` (extract + expand)
4. Create `docs/COMMON_TASKS.md` (extract from CLAUDE.md)
5. Create `ROADMAP.md` (expand current roadmap + new ideas)
6. Rewrite `CLAUDE.md` as terse TOC with links

---

## Verification

1. All links in CLAUDE.md resolve correctly
2. No duplicate content between files
3. CLAUDE.md is ~50 lines (single screen)
4. ROADMAP.md has 10+ future ideas
5. `git diff --stat` shows net reduction in CLAUDE.md
