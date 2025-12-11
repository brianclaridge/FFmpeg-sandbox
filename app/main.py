"""FastAPI application entry point."""

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.config import INPUT_DIR, OUTPUT_DIR, LOGS_DIR
from app.models import PRESETS, PresetLevel
from app.routers import audio, history, download
from app.services.processor import get_input_files


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
    level="INFO",
)
logger.add(
    LOGS_DIR / "app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
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
    version="0.1.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(audio.router)
app.include_router(history.router)
app.include_router(download.router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with audio processor form."""
    input_files = get_input_files(INPUT_DIR)
    presets = [(level.value, config) for level, config in PRESETS.items()]
    default_preset = PRESETS[PresetLevel.MEDIUM]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "input_files": input_files,
            "presets": presets,
            "default_preset": default_preset,
            "delays": "|".join(str(d) for d in default_preset.delays),
            "decays": "|".join(str(d) for d in default_preset.decays),
        },
    )


def run():
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
