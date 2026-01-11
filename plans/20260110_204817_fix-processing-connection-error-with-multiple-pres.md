# Plan: Fix Processing Connection Error with Multiple Presets

**Affects:** `/workspace/app/services/processor.py`

---

## Issue Summary

| Issue | Root Cause | Fix |
|-------|------------|-----|
| "Connection error" when processing multiple presets | Subprocess deadlock - stderr buffer fills, blocks FFmpeg | Drain stderr in background thread |

---

## Root Cause Analysis

**Location:** `/workspace/app/services/processor.py` lines 354-433

The `process_video_with_progress()` function uses `subprocess.Popen()` with both `stdout=PIPE` and `stderr=PIPE`, then only reads stdout in a blocking loop:

```python
process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, ...)
for line in process.stdout:  # Only reads stdout
    # parse progress...
process.wait()
stderr = process.stderr.read()  # Reads AFTER process ends
```

**Why it fails with multiple presets:**
1. Complex filter chains (e.g., "Podcast Ready" + video effects) produce verbose FFmpeg warnings on stderr
2. stderr buffer fills (~64KB)
3. FFmpeg blocks waiting for buffer space
4. Code blocks waiting for stdout
5. **Deadlock** → Browser timeout → "Connection error"

---

## Fix: Drain stderr in Background Thread

Add a background thread to continuously drain stderr while reading stdout for progress.

**File:** `/workspace/app/services/processor.py`

### Step 1: Add threading import (top of file)

```python
import threading
```

### Step 2: Add stderr drain thread (inside process_video_with_progress)

After creating the subprocess, add:

```python
# Background thread to drain stderr and prevent buffer deadlock
stderr_lines = []

def drain_stderr():
    for line in process.stderr:
        stderr_lines.append(line)

stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
stderr_thread.start()
```

### Step 3: Join thread after process.wait()

Replace:
```python
process.wait()
```

With:
```python
process.wait()
stderr_thread.join(timeout=2.0)
```

### Step 4: Update error handling

Replace:
```python
if process.returncode != 0:
    stderr = process.stderr.read()
```

With:
```python
if process.returncode != 0:
    stderr = "".join(stderr_lines)
```

---

## Implementation Steps

1. Add `import threading` at top of processor.py
2. Add stderr drain thread definition inside `process_video_with_progress()`
3. Start thread before stdout loop
4. Join thread after `process.wait()`
5. Collect stderr from `stderr_lines` list instead of `process.stderr.read()`

---

## Verification

1. `task rebuild`
2. Upload a video file
3. Apply "Podcast Ready" audio preset + "VHS Playback" video preset
4. Click Process → Modal shows progress → Completes without "Connection error"
5. Test with 3+ presets combined (e.g., multiple theme presets chained)
