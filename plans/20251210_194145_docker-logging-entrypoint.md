# Plan: Docker Logging and Entrypoint Fix

**Created**: 2024-12-10 19:41:45
**Status**: Pending approval

## Problem Statement

1. Docker-compose logs show errors but `./logs/` directory is empty
2. No custom entrypoint to ensure dependencies are synced at runtime
3. Logging uses relative path which may not resolve correctly in container context

## Root Cause Analysis

- `app/main.py` uses relative path `logs/app.log` for file logging
- Dockerfile CMD runs uvicorn directly without setup steps
- No mechanism to ensure `uv sync` runs if packages are missing at runtime
- Logs directory may not exist or have incorrect permissions

## Implementation Plan

### 1. Fix Logging Configuration (app/main.py)

**Current:**
```python
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)
```

**Updated:**
```python
from app.config import BASE_DIR

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logger.add(
    LOGS_DIR / "app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)
```

### 2. Create Entrypoint Script (docker-entrypoint.sh)

```bash
#!/bin/bash
set -e

# Ensure logs directory exists with correct permissions
mkdir -p /app/logs
chmod 755 /app/logs

# Sync Python dependencies (handles any missing packages)
echo "Syncing Python dependencies..."
uv sync --no-dev

# Start the application
echo "Starting audio processor..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Update Dockerfile

- Add COPY for entrypoint script
- Change CMD to ENTRYPOINT
- Ensure script is executable

### 4. Verify Dual Logging

- stderr handler: INFO level (visible in `docker logs`)
- File handler: DEBUG level (persisted to `./logs/app.log`)

## TODO List

- [ ] Fix logging configuration to use absolute paths
- [ ] Create custom entrypoint script with uv sync and log directory setup
- [ ] Update Dockerfile to use entrypoint script
- [ ] Configure dual logging (stdout + file) properly
- [ ] Test Docker build and verify logs appear in both locations

## Files to Modify

| File | Action |
|------|--------|
| `app/main.py` | Update logging path to use BASE_DIR |
| `docker-entrypoint.sh` | Create new entrypoint script |
| `Dockerfile` | Add entrypoint, copy script |

## Verification Steps

1. `docker-compose build`
2. `docker-compose up`
3. Trigger some requests to generate logs
4. Check `docker logs audio-processor` for stdout output
5. Check `./logs/app.log` for file output
6. Both should contain log entries
