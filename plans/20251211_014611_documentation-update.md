# Documentation Update for Per-File Metadata Changes

## Overview

Update README.md and CLAUDE.md to reflect the per-file metadata architecture implemented in c9867de.

---

## Inaccuracies Found

### README.md

| Line | Current | Should Be |
|------|---------|-----------|
| 12 | "User settings persistence to `.data/user_settings.yml`" | "Per-file metadata in `.data/input/{filename}.yml`" |
| 235-236 | Shows `user_settings.yml` and `history.json` | Remove these, add `{filename}.yml` pattern |
| 248 | "JSON-based history management" | "Per-file YAML metadata" |
| - | Missing | `file_metadata.py` service in structure |
| - | Missing | Anonymized filename format documentation |

### CLAUDE.md

| Line | Current | Should Be |
|------|---------|-----------|
| 24-25 | Shows `user_settings.yml` and `history.json` | Remove, document per-file pattern |
| 37 | "JSON-based history management" | "Per-file YAML metadata" |
| 38 | "User settings YAML persistence" | "Per-file metadata service" |
| 141 | "persist to `.data/user_settings.yml`" | "persist per-file in `.data/input/`" |
| 150 | Same | Same |
| 182 | "History: `.data/history.json`" | Remove, covered by per-file |
| - | Missing | `file_metadata.py` in structure |

---

## Changes

### README.md Updates

1. **Features section** - Replace global settings reference with per-file metadata
2. **Project Structure** - Update `.data/` section:
   ```
   .data/
   ├── input/               # Source files + per-file .yml metadata
   │   ├── yt-abc123.mp4
   │   └── yt-abc123.yml    # Settings, history, source info
   ├── output/              # Processed audio files
   └── logs/                # Application logs
   ```
3. **Services** - Add `file_metadata.py`
4. **Add section** - "Downloaded File Naming" explaining `{source}-{id}.ext` format

### CLAUDE.md Updates

1. **Project Structure** - Same updates as README
2. **Services description** - Update history.py and settings.py descriptions
3. **Add `file_metadata.py`** to services list with description
4. **UI Features section** - Update persistence references
5. **Development Notes** - Update data file locations

---

## Files to Modify

| File | Changes |
|------|---------|
| `README.md` | Update features, project structure, add filename format docs |
| `CLAUDE.md` | Update structure, services, UI features, development notes |

---

## Implementation Steps

- [ ] Update README.md features section (per-file metadata)
- [ ] Update README.md project structure (remove deleted files, add per-file pattern)
- [ ] Add README.md section for downloaded file naming format
- [ ] Update CLAUDE.md project structure
- [ ] Update CLAUDE.md services descriptions
- [ ] Update CLAUDE.md UI features (persistence references)
- [ ] Update CLAUDE.md development notes
