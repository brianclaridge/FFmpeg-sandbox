#!/usr/bin/env pwsh
# Test yt-dlp installation
uv run python -c "import yt_dlp; print(f'yt-dlp version: {yt_dlp.version.__version__}')"
