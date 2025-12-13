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
from app.models import (
    PRESETS, PresetLevel,
    # Audio effects
    VOLUME_PRESETS, VOLUME_PRESETS_BY_STR, VolumePreset,
    TUNNEL_PRESETS, TUNNEL_PRESETS_BY_STR, TunnelPreset,
    FREQUENCY_PRESETS, FREQUENCY_PRESETS_BY_STR, FrequencyPreset,
    SPEED_PRESETS, SPEED_PRESETS_BY_STR, SpeedPreset,
    PITCH_PRESETS, PITCH_PRESETS_BY_STR, PitchPreset,
    NOISE_REDUCTION_PRESETS, NOISE_REDUCTION_PRESETS_BY_STR, NoiseReductionPreset,
    COMPRESSOR_PRESETS, COMPRESSOR_PRESETS_BY_STR, CompressorPreset,
    # Video effects
    BRIGHTNESS_PRESETS, BRIGHTNESS_PRESETS_BY_STR, BrightnessPreset,
    CONTRAST_PRESETS, CONTRAST_PRESETS_BY_STR, ContrastPreset,
    SATURATION_PRESETS, SATURATION_PRESETS_BY_STR, SaturationPreset,
    BLUR_PRESETS, BLUR_PRESETS_BY_STR, BlurPreset,
    SHARPEN_PRESETS, SHARPEN_PRESETS_BY_STR, SharpenPreset,
    TRANSFORM_PRESETS, TRANSFORM_PRESETS_BY_STR, TransformPreset,
)
from app.routers import audio, history, download
from app.services.processor import get_input_files
from app.services.settings import load_user_settings


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

    # Get current preset configs for initial panel render
    try:
        volume_preset = VOLUME_PRESETS[VolumePreset(user_settings.volume.preset)]
    except (ValueError, KeyError):
        volume_preset = VOLUME_PRESETS[VolumePreset.X2]

    try:
        tunnel_preset = TUNNEL_PRESETS[TunnelPreset(user_settings.tunnel.preset)]
    except (ValueError, KeyError):
        tunnel_preset = TUNNEL_PRESETS[TunnelPreset.NONE]

    try:
        frequency_preset = FREQUENCY_PRESETS[FrequencyPreset(user_settings.frequency.preset)]
    except (ValueError, KeyError):
        frequency_preset = FREQUENCY_PRESETS[FrequencyPreset.FLAT]

    # New audio effects
    try:
        speed_preset = SPEED_PRESETS[SpeedPreset(user_settings.speed.preset)]
    except (ValueError, KeyError):
        speed_preset = SPEED_PRESETS[SpeedPreset.NONE]

    try:
        pitch_preset = PITCH_PRESETS[PitchPreset(user_settings.pitch.preset)]
    except (ValueError, KeyError):
        pitch_preset = PITCH_PRESETS[PitchPreset.NONE]

    try:
        noise_reduction_preset = NOISE_REDUCTION_PRESETS[NoiseReductionPreset(user_settings.noise_reduction.preset)]
    except (ValueError, KeyError):
        noise_reduction_preset = NOISE_REDUCTION_PRESETS[NoiseReductionPreset.NONE]

    try:
        compressor_preset = COMPRESSOR_PRESETS[CompressorPreset(user_settings.compressor.preset)]
    except (ValueError, KeyError):
        compressor_preset = COMPRESSOR_PRESETS[CompressorPreset.NONE]

    # Video effects
    try:
        brightness_preset = BRIGHTNESS_PRESETS[BrightnessPreset(user_settings.brightness.preset)]
    except (ValueError, KeyError):
        brightness_preset = BRIGHTNESS_PRESETS[BrightnessPreset.NONE]

    try:
        contrast_preset = CONTRAST_PRESETS[ContrastPreset(user_settings.contrast.preset)]
    except (ValueError, KeyError):
        contrast_preset = CONTRAST_PRESETS[ContrastPreset.NONE]

    try:
        saturation_preset = SATURATION_PRESETS[SaturationPreset(user_settings.saturation.preset)]
    except (ValueError, KeyError):
        saturation_preset = SATURATION_PRESETS[SaturationPreset.NONE]

    try:
        blur_preset = BLUR_PRESETS[BlurPreset(user_settings.blur.preset)]
    except (ValueError, KeyError):
        blur_preset = BLUR_PRESETS[BlurPreset.NONE]

    try:
        sharpen_preset = SHARPEN_PRESETS[SharpenPreset(user_settings.sharpen.preset)]
    except (ValueError, KeyError):
        sharpen_preset = SHARPEN_PRESETS[SharpenPreset.NONE]

    try:
        transform_preset = TRANSFORM_PRESETS[TransformPreset(user_settings.transform.preset)]
    except (ValueError, KeyError):
        transform_preset = TRANSFORM_PRESETS[TransformPreset.NONE]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "input_files": input_files,
            # Effect chain data
            "user_settings": user_settings,
            "current_filename": None,  # No file selected on initial load
            # Audio effect presets
            "volume_presets": VOLUME_PRESETS_BY_STR,
            "tunnel_presets": TUNNEL_PRESETS_BY_STR,
            "frequency_presets": FREQUENCY_PRESETS_BY_STR,
            "speed_presets": SPEED_PRESETS_BY_STR,
            "pitch_presets": PITCH_PRESETS_BY_STR,
            "noise_reduction_presets": NOISE_REDUCTION_PRESETS_BY_STR,
            "compressor_presets": COMPRESSOR_PRESETS_BY_STR,
            # Video effect presets
            "brightness_presets": BRIGHTNESS_PRESETS_BY_STR,
            "contrast_presets": CONTRAST_PRESETS_BY_STR,
            "saturation_presets": SATURATION_PRESETS_BY_STR,
            "blur_presets": BLUR_PRESETS_BY_STR,
            "sharpen_presets": SHARPEN_PRESETS_BY_STR,
            "transform_presets": TRANSFORM_PRESETS_BY_STR,
            # Current audio preset configs
            "volume_current": volume_preset,
            "tunnel_current": tunnel_preset,
            "frequency_current": frequency_preset,
            "speed_current": speed_preset,
            "pitch_current": pitch_preset,
            "noise_reduction_current": noise_reduction_preset,
            "compressor_current": compressor_preset,
            # Current video preset configs
            "brightness_current": brightness_preset,
            "contrast_current": contrast_preset,
            "saturation_current": saturation_preset,
            "blur_current": blur_preset,
            "sharpen_current": sharpen_preset,
            "transform_current": transform_preset,
            # Form defaults based on current settings
            "delays": "|".join(str(d) for d in tunnel_preset.delays),
            "decays": "|".join(str(d) for d in tunnel_preset.decays),
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
