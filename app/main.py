"""FastAPI application entry point."""

import logging
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
    VOLUME_PRESETS, VOLUME_PRESETS_BY_STR, VolumePreset,
    TUNNEL_PRESETS, TUNNEL_PRESETS_BY_STR, TunnelPreset,
    FREQUENCY_PRESETS, FREQUENCY_PRESETS_BY_STR, FrequencyPreset,
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


# Cache bust version (computed once at startup)
CACHE_VERSION = get_git_hash()
templates.env.globals["cache_version"] = CACHE_VERSION
logger.info(f"Cache version: {CACHE_VERSION}")


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

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "input_files": input_files,
            # Effect chain data
            "user_settings": user_settings,
            "volume_presets": VOLUME_PRESETS_BY_STR,
            "tunnel_presets": TUNNEL_PRESETS_BY_STR,
            "frequency_presets": FREQUENCY_PRESETS_BY_STR,
            "current_filename": None,  # No file selected on initial load
            # Accordion: current preset configs for each category
            "volume_current": volume_preset,
            "tunnel_current": tunnel_preset,
            "frequency_current": frequency_preset,
            # Form defaults based on current settings
            "delays": "|".join(str(d) for d in tunnel_preset.delays),
            "decays": "|".join(str(d) for d in tunnel_preset.decays),
        },
    )


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
