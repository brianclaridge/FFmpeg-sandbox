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

    # Get preset dictionaries from YAML
    volume_presets = get_volume_presets()
    tunnel_presets = get_tunnel_presets()
    frequency_presets = get_frequency_presets()
    speed_presets = get_speed_presets()
    pitch_presets = get_pitch_presets()
    noise_reduction_presets = get_noise_reduction_presets()
    compressor_presets = get_compressor_presets()
    brightness_presets = get_brightness_presets()
    contrast_presets = get_contrast_presets()
    saturation_presets = get_saturation_presets()
    blur_presets = get_blur_presets()
    sharpen_presets = get_sharpen_presets()
    transform_presets = get_transform_presets()

    # Get current preset configs for initial panel render (with fallbacks)
    volume_current = volume_presets.get(user_settings.volume.preset) or volume_presets.get("none")
    tunnel_current = tunnel_presets.get(user_settings.tunnel.preset) or tunnel_presets.get("none")
    frequency_current = frequency_presets.get(user_settings.frequency.preset) or frequency_presets.get("none")
    speed_current = speed_presets.get(user_settings.speed.preset) or speed_presets.get("none")
    pitch_current = pitch_presets.get(user_settings.pitch.preset) or pitch_presets.get("none")
    noise_reduction_current = noise_reduction_presets.get(user_settings.noise_reduction.preset) or noise_reduction_presets.get("none")
    compressor_current = compressor_presets.get(user_settings.compressor.preset) or compressor_presets.get("none")
    brightness_current = brightness_presets.get(user_settings.brightness.preset) or brightness_presets.get("none")
    contrast_current = contrast_presets.get(user_settings.contrast.preset) or contrast_presets.get("none")
    saturation_current = saturation_presets.get(user_settings.saturation.preset) or saturation_presets.get("none")
    blur_current = blur_presets.get(user_settings.blur.preset) or blur_presets.get("none")
    sharpen_current = sharpen_presets.get(user_settings.sharpen.preset) or sharpen_presets.get("none")
    transform_current = transform_presets.get(user_settings.transform.preset) or transform_presets.get("none")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "input_files": input_files,
            # Effect chain data
            "user_settings": user_settings,
            "current_filename": None,  # No file selected on initial load
            # Audio effect presets
            "volume_presets": volume_presets,
            "tunnel_presets": tunnel_presets,
            "frequency_presets": frequency_presets,
            "speed_presets": speed_presets,
            "pitch_presets": pitch_presets,
            "noise_reduction_presets": noise_reduction_presets,
            "compressor_presets": compressor_presets,
            # Video effect presets
            "brightness_presets": brightness_presets,
            "contrast_presets": contrast_presets,
            "saturation_presets": saturation_presets,
            "blur_presets": blur_presets,
            "sharpen_presets": sharpen_presets,
            "transform_presets": transform_presets,
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
