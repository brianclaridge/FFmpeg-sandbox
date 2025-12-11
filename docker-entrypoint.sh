#!/bin/bash
set -e

# Ensure logs directory exists with correct permissions
mkdir -p /app/logs
chmod 755 /app/logs

# Ensure data directories exist
mkdir -p /app/data/input /app/data/output

# Sync Python dependencies (handles any missing packages at runtime)
echo "[entrypoint] Syncing Python dependencies..."
uv sync --no-dev

echo "[entrypoint] Starting audio processor..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
