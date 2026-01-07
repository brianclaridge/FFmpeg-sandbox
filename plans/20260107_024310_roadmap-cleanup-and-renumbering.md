# Plan: Roadmap Cleanup and Renumbering

**Affects:** `/workspace/CLAUDE.md`

---

## Objective

Reorganize the Development Roadmap in CLAUDE.md:
1. Move completed phases to a "Completed Phases" section
2. Renumber remaining phases sequentially (1, 2, 3...)
3. Keep lower priority items at the end

---

## Current State

| Phase | Status |
|-------|--------|
| 13: Audio Filter QA | Backend ready |
| 14: Shortcut Management | **Complete** |
| 15: Batch Processing | Not started |
| 20: Output Format Options | Not started |
| 21: Presets Tab + Terminology | **Complete** |
| 16-19 | Lower priority |

---

## New Structure

### Active Phases (renumbered)
1. **Phase 1: Audio Filter QA** (was 13)
2. **Phase 2: Batch Processing** (was 15)
3. **Phase 3: Output Format Options** (was 20)

### Lower Priority
4. **Phase 4: Waveform Visualization** (was 16)
5. **Phase 5: Performance** (was 17)
6. **Phase 6: Mobile Responsiveness** (was 18)
7. **Phase 7: Keyboard Shortcuts** (was 19)

### Completed Phases (new section)
- Phase 14: Shortcut Management
- Phase 21: Presets Tab + Terminology Refactor

---

## Implementation

1. Edit `/workspace/CLAUDE.md` Development Roadmap section
2. Create "Completed Phases" section at the end
3. Renumber active phases 1-3
4. Renumber lower priority phases 4-7
5. Update status labels
