"""Audio processing router."""

from pathlib import Path

import subprocess
import tempfile
import os

from fastapi import APIRouter, Form, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.config import INPUT_DIR, OUTPUT_DIR, config
from app.models import (
    PresetLevel, PRESETS,
    VolumePreset, VOLUME_PRESETS, VOLUME_PRESETS_BY_STR,
    TunnelPreset, TUNNEL_PRESETS, TUNNEL_PRESETS_BY_STR,
    FrequencyPreset, FREQUENCY_PRESETS, FREQUENCY_PRESETS_BY_STR,
)
from app.services.settings import (
    load_user_settings,
    update_category_preset,
    update_active_category,
)
from app.services.processor import process_audio, get_input_files, get_file_duration, format_duration_ms, get_file_metadata
from app.services.history import add_history_entry

ALLOWED_EXTENSIONS = set(config.audio.allowed_extensions)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/process", response_class=HTMLResponse)
async def process(
    request: Request,
    input_file: str = Form(...),
    start_time: str = Form(config.audio.default_start_time),
    end_time: str = Form(config.audio.default_end_time),
    preset: str = Form(config.audio.default_preset),
    volume: float = Form(2.0),
    highpass: int = Form(100),
    lowpass: int = Form(4500),
    delays: str = Form("15|25|35|50"),
    decays: str = Form("0.35|0.3|0.25|0.2"),
    volume_preset: str = Form("2x"),
    tunnel_preset: str = Form("none"),
    frequency_preset: str = Form("flat"),
):
    """Process audio and return preview partial."""
    input_path = INPUT_DIR / input_file

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found")

    # Save preset selections to per-file .yml metadata
    if input_file:
        update_category_preset("volume", volume_preset, input_file)
        update_category_preset("tunnel", tunnel_preset, input_file)
        update_category_preset("frequency", frequency_preset, input_file)

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
            volume_preset=volume_preset,
            tunnel_preset=tunnel_preset,
            frequency_preset=frequency_preset,
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
async def get_sliders(request: Request, preset: str = config.audio.default_preset):
    """Get slider form populated with preset values."""
    try:
        preset_level = PresetLevel(preset)
        preset_config = PRESETS[preset_level]
    except ValueError:
        preset_level = PresetLevel.NONE
        preset_config = PRESETS[preset_level]

    return templates.TemplateResponse(
        "partials/slider_form.html",
        {
            "request": request,
            "preset": preset_config,
            "delays": "|".join(str(d) for d in preset_config.delays),
            "decays": "|".join(str(d) for d in preset_config.decays),
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
    """Get file metadata including duration."""
    file_path = INPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    metadata = get_file_metadata(file_path)

    if "duration_ms" not in metadata:
        # Fallback to basic duration detection
        duration_ms = get_file_duration(file_path)
        if duration_ms is None:
            raise HTTPException(status_code=500, detail="Could not determine duration")
        metadata["duration_ms"] = duration_ms
        metadata["duration_formatted"] = format_duration_ms(duration_ms)

    return JSONResponse(metadata)


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
            "-q:a", config.audio.mp3_quality,
            tmp_path,
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=config.audio.preview_timeout)

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


@router.get("/clip-video-preview")
async def clip_video_preview(filename: str, start: str, end: str):
    """
    Generate a video preview clip on-the-fly for the video modal.
    """
    input_path = INPUT_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Check if it's a video file
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
    ext = input_path.suffix.lower()
    if ext not in video_extensions:
        raise HTTPException(status_code=400, detail="Not a video file")

    # Create temporary file for preview
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", start,
            "-to", end,
            "-i", str(input_path),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            tmp_path,
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=config.audio.preview_timeout)

        if result.returncode != 0:
            logger.warning(f"Video preview generation failed: {result.stderr}")
            raise HTTPException(status_code=500, detail="Video preview generation failed")

        def iterfile():
            with open(tmp_path, "rb") as f:
                yield from f
            os.unlink(tmp_path)

        return StreamingResponse(
            iterfile(),
            media_type="video/mp4",
            headers={"Content-Disposition": "inline; filename=preview.mp4"}
        )
    except subprocess.TimeoutExpired:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=408, detail="Video preview generation timed out")
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.exception("Video preview generation error")
        raise HTTPException(status_code=500, detail=str(e))


# ============ EFFECT CHAIN ENDPOINTS ============

def _get_accordion_context(user_settings, filename: str | None = None) -> dict:
    """Build context dict for accordion template."""
    # Get current preset configs for each category
    try:
        volume_current = VOLUME_PRESETS[VolumePreset(user_settings.volume.preset)]
    except (ValueError, KeyError):
        volume_current = VOLUME_PRESETS[VolumePreset("2x")]

    try:
        tunnel_current = TUNNEL_PRESETS[TunnelPreset(user_settings.tunnel.preset)]
    except (ValueError, KeyError):
        tunnel_current = TUNNEL_PRESETS[TunnelPreset("none")]

    try:
        frequency_current = FREQUENCY_PRESETS[FrequencyPreset(user_settings.frequency.preset)]
    except (ValueError, KeyError):
        frequency_current = FREQUENCY_PRESETS[FrequencyPreset("flat")]

    return {
        "user_settings": user_settings,
        "volume_presets": VOLUME_PRESETS_BY_STR,
        "tunnel_presets": TUNNEL_PRESETS_BY_STR,
        "frequency_presets": FREQUENCY_PRESETS_BY_STR,
        "volume_current": volume_current,
        "tunnel_current": tunnel_current,
        "frequency_current": frequency_current,
        "current_filename": filename,
    }


@router.get("/partials/effect-chain", response_class=HTMLResponse)
async def get_effect_chain(request: Request, filename: str | None = None):
    """Get the full effect chain UI component (accordion)."""
    user_settings = load_user_settings(filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/effect_chain_accordion.html", context)


@router.get("/partials/category-panel/{category}", response_class=HTMLResponse)
async def get_category_panel(request: Request, category: str, filename: str | None = None):
    """Get the control panel for a specific category (legacy endpoint - returns accordion)."""
    if category not in ("volume", "tunnel", "frequency"):
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/effect_chain_accordion.html", context)


@router.post("/partials/category-preset/{category}/{preset}", response_class=HTMLResponse)
async def set_category_preset(request: Request, category: str, preset: str, filename: str = Form("")):
    """Update a category's preset selection (legacy endpoint - redirects to accordion)."""
    user_settings = update_category_preset(category, preset, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/effect_chain_accordion.html", context)


@router.get("/partials/accordion/{category}", response_class=HTMLResponse)
async def get_accordion_section(request: Request, category: str, filename: str | None = None):
    """Expand an accordion section (collapses others)."""
    if category not in ("volume", "tunnel", "frequency"):
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    return templates.TemplateResponse("partials/effect_chain_accordion.html", context)


@router.post("/partials/accordion-preset/{category}/{preset}", response_class=HTMLResponse)
async def set_accordion_preset(request: Request, category: str, preset: str, filename: str = Form("")):
    """Update a category's preset and return updated accordion."""
    if category not in ("volume", "tunnel", "frequency"):
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_category_preset(category, preset, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    return templates.TemplateResponse("partials/effect_chain_accordion.html", context)
