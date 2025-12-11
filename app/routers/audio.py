"""Audio processing router."""

from pathlib import Path

import subprocess
import tempfile
import os

from fastapi import APIRouter, Form, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.config import INPUT_DIR, OUTPUT_DIR
from app.models import PresetLevel, PRESETS
from app.services.processor import process_audio, get_input_files, get_file_duration, format_duration_ms
from app.services.history import add_history_entry

ALLOWED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".mp3", ".wav", ".flac", ".m4a", ".ogg"}

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


@router.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Upload a file to the input directory."""
    if not file.filename:
        return templates.TemplateResponse(
            "partials/upload_status.html",
            {"request": request, "error": "No file selected", "success": False},
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return templates.TemplateResponse(
            "partials/upload_status.html",
            {
                "request": request,
                "error": f"Invalid file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                "success": False,
            },
        )

    safe_filename = Path(file.filename).name
    dest_path = INPUT_DIR / safe_filename

    try:
        content = await file.read()
        dest_path.write_bytes(content)
        logger.info(f"Uploaded file: {safe_filename} ({len(content)} bytes)")

        input_files = get_input_files(INPUT_DIR)
        return templates.TemplateResponse(
            "partials/upload_status.html",
            {
                "request": request,
                "success": True,
                "filename": safe_filename,
                "input_files": input_files,
            },
        )
    except Exception as e:
        logger.exception("Upload failed")
        return templates.TemplateResponse(
            "partials/upload_status.html",
            {"request": request, "error": str(e), "success": False},
        )


@router.get("/duration/{filename}")
async def get_duration(filename: str):
    """Get file duration in milliseconds."""
    file_path = INPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    duration_ms = get_file_duration(file_path)

    if duration_ms is None:
        raise HTTPException(status_code=500, detail="Could not determine duration")

    return JSONResponse({
        "filename": filename,
        "duration_ms": duration_ms,
        "duration_formatted": format_duration_ms(duration_ms),
    })


@router.get("/clip-preview")
async def clip_preview(filename: str, start: str, end: str):
    """
    Generate a preview clip on-the-fly for the range slider.
    Uses streamcopy for speed when possible.
    """
    input_path = INPUT_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Create temporary file for preview
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", start,
            "-to", end,
            "-i", str(input_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "4",
            tmp_path,
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if result.returncode != 0:
            logger.warning(f"Preview generation failed: {result.stderr}")
            raise HTTPException(status_code=500, detail="Preview generation failed")

        def iterfile():
            with open(tmp_path, "rb") as f:
                yield from f
            os.unlink(tmp_path)

        return StreamingResponse(
            iterfile(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=preview.mp3"}
        )
    except subprocess.TimeoutExpired:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=408, detail="Preview generation timed out")
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.exception("Preview generation error")
        raise HTTPException(status_code=500, detail=str(e))
