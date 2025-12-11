"""Audio processing router."""

from pathlib import Path

from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.config import INPUT_DIR, OUTPUT_DIR
from app.models import PresetLevel, PRESETS
from app.services.processor import process_audio, get_input_files
from app.services.history import add_history_entry

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/process", response_class=HTMLResponse)
async def process(
    request: Request,
    input_file: str = Form(...),
    start_time: str = Form("00:00:00"),
    end_time: str = Form("00:00:06"),
    preset: str = Form("medium"),
    volume: float = Form(2.0),
    highpass: int = Form(100),
    lowpass: int = Form(4500),
    delays: str = Form("15|25|35|50"),
    decays: str = Form("0.35|0.3|0.25|0.2"),
):
    """Process audio and return preview partial."""
    input_path = INPUT_DIR / input_file

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found")

    try:
        output_path = process_audio(
            input_file=input_path,
            start_time=start_time,
            end_time=end_time,
            volume=volume,
            highpass=highpass,
            lowpass=lowpass,
            delays=delays,
            decays=decays,
        )

        add_history_entry(
            input_file=input_file,
            output_file=output_path.name,
            start_time=start_time,
            end_time=end_time,
            preset=preset,
            volume=volume,
            highpass=highpass,
            lowpass=lowpass,
            delays=delays,
            decays=decays,
        )

        return templates.TemplateResponse(
            "partials/preview.html",
            {
                "request": request,
                "output_file": output_path.name,
                "success": True,
            },
        )
    except Exception as e:
        logger.exception("Processing failed")
        return templates.TemplateResponse(
            "partials/preview.html",
            {
                "request": request,
                "error": str(e),
                "success": False,
            },
        )


@router.get("/preview/{filename}")
async def preview_audio(filename: str):
    """Serve processed audio file."""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename,
    )


@router.get("/partials/sliders", response_class=HTMLResponse)
async def get_sliders(request: Request, preset: str = "medium"):
    """Get slider form populated with preset values."""
    try:
        preset_level = PresetLevel(preset)
        config = PRESETS[preset_level]
    except ValueError:
        preset_level = PresetLevel.MEDIUM
        config = PRESETS[preset_level]

    return templates.TemplateResponse(
        "partials/slider_form.html",
        {
            "request": request,
            "preset": config,
            "delays": "|".join(str(d) for d in config.delays),
            "decays": "|".join(str(d) for d in config.decays),
        },
    )
