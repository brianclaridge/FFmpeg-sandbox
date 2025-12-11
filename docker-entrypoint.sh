#!/bin/bash
set -e

# Ensure data directories exist with correct permissions
mkdir -p /app/.data/input /app/.data/output /app/.data/logs
chmod 755 /app/.data/logs

# Sync Python dependencies (handles any missing packages at runtime)
echo "[entrypoint] Syncing Python dependencies..."
uv sync --no-dev

echo "[entrypoint] Starting audio processor..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
