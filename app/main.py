"""FastAPI application entry point."""

import logging
import os
import subprocess
import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.config import INPUT_DIR, OUTPUT_DIR, LOGS_DIR, config
from app.models import PRESETS, PresetLevel
from app.routers import audio, history, download
from app.services import get_input_files
from app.services.settings import load_user_settings
from app.services.presets import (
    load_presets,
    get_volume_presets,
    get_tunnel_presets,
    get_frequency_presets,
    get_speed_presets,
    get_pitch_presets,
    get_noise_reduction_presets,
    get_compressor_presets,
    get_brightness_presets,
    get_contrast_presets,
    get_saturation_presets,
    get_blur_presets,
    get_sharpen_presets,
    get_transform_presets,
)


class InterceptHandler(logging.Handler):
    """Intercept standard logging and route to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=config.logging.stderr_level,
)
logger.add(
    LOGS_DIR / "app.log",
    rotation=config.logging.rotation,
    retention=config.logging.retention,
    level=config.logging.file_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

# Intercept uvicorn and other standard loggers
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
    log = logging.getLogger(name)
    log.handlers = [InterceptHandler()]
    log.propagate = False

logger.info("Audio Processor starting up")

# Load presets from YAML file
load_presets()

# Load theme presets (VHS, Vinyl, etc.)
from app.services.presets_themes import load_theme_presets
load_theme_presets()

app = FastAPI(
    title="Audio Processor",
    description="Extract and process audio with tunnel effects",
    version=config.server.version,
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(audio.router)
app.include_router(history.router)
app.include_router(download.router)

templates = Jinja2Templates(directory="app/templates")


def get_git_hash() -> str:
    """Get current git commit short hash for cache busting."""
    # Check environment variable first (set at Docker build time)
    env_hash = os.environ.get("GIT_HASH", "")
    if env_hash and env_hash != "dev":
        return env_hash
    # Fall back to git command (for local development)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "dev"


def get_git_commit_date() -> str:
    """Get current git commit date in yyyy.mm.dd format."""
    # Check environment variable first (set at Docker build time)
    env_date = os.environ.get("GIT_DATE", "")
    if env_date:
        return env_date
    # Fall back to git command (for local development)
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=format:%Y.%m.%d"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


# Cache bust version (computed once at startup)
CACHE_VERSION = get_git_hash()
COMMIT_DATE = get_git_commit_date()
templates.env.globals["cache_version"] = CACHE_VERSION
templates.env.globals["commit_hash"] = CACHE_VERSION
templates.env.globals["commit_date"] = COMMIT_DATE
logger.info(f"Version: {COMMIT_DATE} ({CACHE_VERSION})")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with audio processor form."""
    input_files = get_input_files(INPUT_DIR)
    user_settings = load_user_settings()

    # Get shortcut dictionaries from YAML
    volume_shortcuts = get_volume_presets()
    tunnel_shortcuts = get_tunnel_presets()
    frequency_shortcuts = get_frequency_presets()
    speed_shortcuts = get_speed_presets()
    pitch_shortcuts = get_pitch_presets()
    noise_reduction_shortcuts = get_noise_reduction_presets()
    compressor_shortcuts = get_compressor_presets()
    brightness_shortcuts = get_brightness_presets()
    contrast_shortcuts = get_contrast_presets()
    saturation_shortcuts = get_saturation_presets()
    blur_shortcuts = get_blur_presets()
    sharpen_shortcuts = get_sharpen_presets()
    transform_shortcuts = get_transform_presets()

    # Get theme presets for Presets tab
    from app.services.presets_themes import get_video_theme_presets, get_audio_theme_presets
    video_theme_presets = get_video_theme_presets()
    audio_theme_presets = get_audio_theme_presets()

    # Get current shortcut configs for initial panel render (with fallbacks)
    volume_current = volume_shortcuts.get(user_settings.volume.preset) or volume_shortcuts.get("none")
    tunnel_current = tunnel_shortcuts.get(user_settings.tunnel.preset) or tunnel_shortcuts.get("none")
    frequency_current = frequency_shortcuts.get(user_settings.frequency.preset) or frequency_shortcuts.get("none")
    speed_current = speed_shortcuts.get(user_settings.speed.preset) or speed_shortcuts.get("none")
    pitch_current = pitch_shortcuts.get(user_settings.pitch.preset) or pitch_shortcuts.get("none")
    noise_reduction_current = noise_reduction_shortcuts.get(user_settings.noise_reduction.preset) or noise_reduction_shortcuts.get("none")
    compressor_current = compressor_shortcuts.get(user_settings.compressor.preset) or compressor_shortcuts.get("none")
    brightness_current = brightness_shortcuts.get(user_settings.brightness.preset) or brightness_shortcuts.get("none")
    contrast_current = contrast_shortcuts.get(user_settings.contrast.preset) or contrast_shortcuts.get("none")
    saturation_current = saturation_shortcuts.get(user_settings.saturation.preset) or saturation_shortcuts.get("none")
    blur_current = blur_shortcuts.get(user_settings.blur.preset) or blur_shortcuts.get("none")
    sharpen_current = sharpen_shortcuts.get(user_settings.sharpen.preset) or sharpen_shortcuts.get("none")
    transform_current = transform_shortcuts.get(user_settings.transform.preset) or transform_shortcuts.get("none")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "input_files": input_files,
            # Effect chain data
            "user_settings": user_settings,
            "current_filename": None,  # No file selected on initial load
            # Audio effect shortcuts
            "volume_shortcuts": volume_shortcuts,
            "tunnel_shortcuts": tunnel_shortcuts,
            "frequency_shortcuts": frequency_shortcuts,
            "speed_shortcuts": speed_shortcuts,
            "pitch_shortcuts": pitch_shortcuts,
            "noise_reduction_shortcuts": noise_reduction_shortcuts,
            "compressor_shortcuts": compressor_shortcuts,
            # Video effect shortcuts
            "brightness_shortcuts": brightness_shortcuts,
            "contrast_shortcuts": contrast_shortcuts,
            "saturation_shortcuts": saturation_shortcuts,
            "blur_shortcuts": blur_shortcuts,
            "sharpen_shortcuts": sharpen_shortcuts,
            "transform_shortcuts": transform_shortcuts,
            # Current audio preset configs
            "volume_current": volume_current,
            "tunnel_current": tunnel_current,
            "frequency_current": frequency_current,
            "speed_current": speed_current,
            "pitch_current": pitch_current,
            "noise_reduction_current": noise_reduction_current,
            "compressor_current": compressor_current,
            # Current video preset configs
            "brightness_current": brightness_current,
            "contrast_current": contrast_current,
            "saturation_current": saturation_current,
            "blur_current": blur_current,
            "sharpen_current": sharpen_current,
            "transform_current": transform_current,
            # Form defaults based on current settings
            "delays": "|".join(str(d) for d in tunnel_current.delays),
            "decays": "|".join(str(d) for d in tunnel_current.decays),
            # Theme presets for Presets tab
            "video_theme_presets": video_theme_presets,
            "audio_theme_presets": audio_theme_presets,
            "applied_video_theme": user_settings.applied_video_theme,
            "applied_audio_theme": user_settings.applied_audio_theme,
        },
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}


def run():
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
    )


if __name__ == "__main__":
    run()
