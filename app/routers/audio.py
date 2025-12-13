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
from app.models import PresetLevel, PRESETS
from app.services.presets import (
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
from app.services.settings import (
    load_user_settings,
    update_category_preset,
    update_active_category,
    update_active_tab,
)
from app.services import (
    process_audio,
    process_audio_with_effects,
    process_video_with_effects,
    get_input_files,
    get_file_duration,
    format_duration_ms,
    get_file_metadata,
    build_audio_filter_chain,
    build_video_filter_chain,
)
from app.services.file_metadata import load_file_metadata
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
):
    """Process audio/video and return preview partial."""
    input_path = INPUT_DIR / input_file

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found")

    # Load user settings from per-file YAML
    user_settings = load_user_settings(input_file)

    # Get preset dictionaries
    volume_presets = get_volume_presets()
    tunnel_presets = get_tunnel_presets()
    frequency_presets = get_frequency_presets()
    speed_presets = get_speed_presets()
    pitch_presets = get_pitch_presets()
    noise_presets = get_noise_reduction_presets()
    compressor_presets = get_compressor_presets()
    brightness_presets = get_brightness_presets()
    contrast_presets = get_contrast_presets()
    saturation_presets = get_saturation_presets()
    blur_presets = get_blur_presets()
    sharpen_presets = get_sharpen_presets()
    transform_presets = get_transform_presets()

    # Lookup all preset configurations from user settings (with fallbacks)
    volume_config = volume_presets.get(user_settings.volume.preset) or volume_presets["none"]
    tunnel_config = tunnel_presets.get(user_settings.tunnel.preset) or tunnel_presets["none"]
    frequency_config = frequency_presets.get(user_settings.frequency.preset) or frequency_presets["none"]
    speed_config = speed_presets.get(user_settings.speed.preset) or speed_presets["none"]
    pitch_config = pitch_presets.get(user_settings.pitch.preset) or pitch_presets["none"]
    noise_config = noise_presets.get(user_settings.noise_reduction.preset) or noise_presets["none"]
    comp_config = compressor_presets.get(user_settings.compressor.preset) or compressor_presets["none"]

    # Video effect presets
    brightness_config = brightness_presets.get(user_settings.brightness.preset) or brightness_presets["none"]
    contrast_config = contrast_presets.get(user_settings.contrast.preset) or contrast_presets["none"]
    saturation_config = saturation_presets.get(user_settings.saturation.preset) or saturation_presets["none"]
    blur_config = blur_presets.get(user_settings.blur.preset) or blur_presets["none"]
    sharpen_config = sharpen_presets.get(user_settings.sharpen.preset) or sharpen_presets["none"]
    transform_config = transform_presets.get(user_settings.transform.preset) or transform_presets["none"]

    # Build audio filter chain with all effects (speed is linked)
    delays_str = "|".join(str(d) for d in tunnel_config.delays)
    decays_str = "|".join(str(d) for d in tunnel_config.decays)

    audio_filter = build_audio_filter_chain(
        volume=volume_config.volume,
        highpass=frequency_config.highpass,
        lowpass=frequency_config.lowpass,
        delays=delays_str,
        decays=decays_str,
        speed=speed_config.speed,
        pitch_semitones=pitch_config.semitones,
        noise_floor=noise_config.noise_floor,
        noise_reduction=noise_config.noise_reduction,
        comp_threshold=comp_config.threshold,
        comp_ratio=comp_config.ratio,
        comp_attack=comp_config.attack,
        comp_release=comp_config.release,
        comp_makeup=comp_config.makeup,
    )

    # Check if input is a video file
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
    is_video = input_path.suffix.lower() in video_extensions

    # Check if any video effects are active
    video_effects_active = (
        brightness_config.brightness != 0.0 or
        contrast_config.contrast != 1.0 or
        saturation_config.saturation != 1.0 or
        blur_config.sigma > 0 or
        sharpen_config.amount > 0 or
        transform_config.filter != "" or
        speed_config.speed != 1.0  # Speed affects video PTS too
    )

    try:
        if is_video and video_effects_active:
            # Build video filter chain (with same speed for sync)
            video_filter = build_video_filter_chain(
                brightness=brightness_config.brightness,
                contrast=contrast_config.contrast,
                saturation=saturation_config.saturation,
                blur_sigma=blur_config.sigma,
                sharpen_amount=sharpen_config.amount,
                transform=transform_config.filter,
                speed=speed_config.speed,
            )

            output_path = process_video_with_effects(
                input_file=input_path,
                start_time=start_time,
                end_time=end_time,
                audio_filter=audio_filter,
                video_filter=video_filter,
                output_format="mp4",
            )
        else:
            # Audio-only output with full filter chain (all 7 audio effects)
            output_path = process_audio_with_effects(
                input_file=input_path,
                start_time=start_time,
                end_time=end_time,
                audio_filter=audio_filter,
                output_format="mp3",
            )

        add_history_entry(
            input_file=input_file,
            output_file=output_path.name,
            start_time=start_time,
            end_time=end_time,
            preset=user_settings.tunnel.preset,
            volume=volume_config.volume,
            highpass=frequency_config.highpass,
            lowpass=frequency_config.lowpass,
            delays=delays_str,
            decays=decays_str,
            volume_preset=user_settings.volume.preset,
            tunnel_preset=user_settings.tunnel.preset,
            frequency_preset=user_settings.frequency.preset,
        )

        return templates.TemplateResponse(
            "partials/preview.html",
            {
                "request": request,
                "output_file": output_path.name,
                "is_video": output_path.suffix.lower() in {".mp4", ".webm", ".mkv"},
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


@router.post("/extract", response_class=HTMLResponse)
async def extract(
    request: Request,
    input_file: str = Form(...),
    start_time: str = Form(config.audio.default_start_time),
    end_time: str = Form(config.audio.default_end_time),
):
    """Extract audio from video without applying effects."""
    input_path = INPUT_DIR / input_file

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found")

    try:
        # Extract audio with neutral settings (no effects)
        output_path = process_audio(
            input_file=input_path,
            start_time=start_time,
            end_time=end_time,
            volume=1.0,        # No volume change
            highpass=20,       # Minimal high-pass (full bass)
            lowpass=20000,     # Minimal low-pass (full treble)
            delays="1",        # Minimal delay
            decays="0",        # No echo effect
        )

        add_history_entry(
            input_file=input_file,
            output_file=output_path.name,
            start_time=start_time,
            end_time=end_time,
            preset="extract",
            volume=1.0,
            highpass=20,
            lowpass=20000,
            delays="1",
            decays="0",
            volume_preset="none",
            tunnel_preset="none",
            frequency_preset="none",
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
        logger.exception("Extraction failed")
        return templates.TemplateResponse(
            "partials/preview.html",
            {
                "request": request,
                "error": str(e),
                "success": False,
            },
        )


@router.get("/preview/{filename}")
async def preview_file(filename: str):
    """Serve processed audio or video file."""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Detect media type from extension
    ext = file_path.suffix.lower()
    media_types = {
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mkv": "video/x-matroska",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type, filename=filename)


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
    """Get file metadata including duration, title, and tags."""
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

    # Load per-file YAML metadata for title and tags (from yt-dlp downloads)
    file_meta = load_file_metadata(filename)
    source = file_meta.get("source", {})
    metadata["title"] = source.get("title", "")
    metadata["tags"] = source.get("tags", [])
    metadata["uploader"] = source.get("uploader", "")
    metadata["uploader_url"] = source.get("uploader_url", "")
    metadata["source_url"] = source.get("url", "")

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

    # Get current preset configs for each category (with fallbacks)
    volume_current = volume_presets.get(user_settings.volume.preset) or volume_presets["none"]
    tunnel_current = tunnel_presets.get(user_settings.tunnel.preset) or tunnel_presets["none"]
    frequency_current = frequency_presets.get(user_settings.frequency.preset) or frequency_presets["none"]
    speed_current = speed_presets.get(user_settings.speed.preset) or speed_presets["none"]
    pitch_current = pitch_presets.get(user_settings.pitch.preset) or pitch_presets["none"]
    noise_reduction_current = noise_reduction_presets.get(user_settings.noise_reduction.preset) or noise_reduction_presets["none"]
    compressor_current = compressor_presets.get(user_settings.compressor.preset) or compressor_presets["none"]

    # Video effects
    brightness_current = brightness_presets.get(user_settings.brightness.preset) or brightness_presets["none"]
    contrast_current = contrast_presets.get(user_settings.contrast.preset) or contrast_presets["none"]
    saturation_current = saturation_presets.get(user_settings.saturation.preset) or saturation_presets["none"]
    blur_current = blur_presets.get(user_settings.blur.preset) or blur_presets["none"]
    sharpen_current = sharpen_presets.get(user_settings.sharpen.preset) or sharpen_presets["none"]
    transform_current = transform_presets.get(user_settings.transform.preset) or transform_presets["none"]

    return {
        "user_settings": user_settings,
        # Audio presets
        "volume_presets": volume_presets,
        "tunnel_presets": tunnel_presets,
        "frequency_presets": frequency_presets,
        "speed_presets": speed_presets,
        "pitch_presets": pitch_presets,
        "noise_reduction_presets": noise_reduction_presets,
        "compressor_presets": compressor_presets,
        # Video presets
        "brightness_presets": brightness_presets,
        "contrast_presets": contrast_presets,
        "saturation_presets": saturation_presets,
        "blur_presets": blur_presets,
        "sharpen_presets": sharpen_presets,
        "transform_presets": transform_presets,
        # Current values
        "volume_current": volume_current,
        "tunnel_current": tunnel_current,
        "frequency_current": frequency_current,
        "speed_current": speed_current,
        "pitch_current": pitch_current,
        "noise_reduction_current": noise_reduction_current,
        "compressor_current": compressor_current,
        "brightness_current": brightness_current,
        "contrast_current": contrast_current,
        "saturation_current": saturation_current,
        "blur_current": blur_current,
        "sharpen_current": sharpen_current,
        "transform_current": transform_current,
        "current_filename": filename,
    }


@router.get("/partials/effect-chain", response_class=HTMLResponse)
async def get_effect_chain(request: Request, filename: str | None = None):
    """Get the full effect chain UI component (tabs with accordion)."""
    user_settings = load_user_settings(filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/effects_tabs.html", context)


@router.get("/partials/effects-tab/{tab}", response_class=HTMLResponse)
async def get_effects_tab(request: Request, tab: str, filename: str | None = None):
    """Switch between Audio and Video effects tabs."""
    if tab not in ("audio", "video"):
        raise HTTPException(status_code=404, detail="Tab not found")

    user_settings = update_active_tab(tab, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    # Return full tabs container so tab buttons update their active state
    return templates.TemplateResponse("partials/effects_tabs.html", context)


AUDIO_CATEGORIES = ("volume", "tunnel", "frequency", "speed", "pitch", "noise_reduction", "compressor")
VIDEO_CATEGORIES = ("brightness", "contrast", "saturation", "blur", "sharpen", "transform")
ALL_CATEGORIES = AUDIO_CATEGORIES + VIDEO_CATEGORIES


@router.get("/partials/category-panel/{category}", response_class=HTMLResponse)
async def get_category_panel(request: Request, category: str, filename: str | None = None):
    """Get the control panel for a specific category (legacy endpoint - returns accordion)."""
    if category not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/effects_audio_accordion.html", context)


@router.post("/partials/category-preset/{category}/{preset}", response_class=HTMLResponse)
async def set_category_preset(request: Request, category: str, preset: str, filename: str = Form("")):
    """Update a category's preset selection (legacy endpoint - redirects to accordion)."""
    user_settings = update_category_preset(category, preset, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/effects_audio_accordion.html", context)


@router.get("/partials/accordion/{category}", response_class=HTMLResponse)
async def get_accordion_section(request: Request, category: str, filename: str | None = None):
    """Expand an accordion section (collapses others)."""
    if category not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    # Return correct template based on category type
    if category in VIDEO_CATEGORIES:
        return templates.TemplateResponse("partials/effects_video_accordion.html", context)
    return templates.TemplateResponse("partials/effects_audio_accordion.html", context)


@router.post("/partials/accordion-preset/{category}/{preset}", response_class=HTMLResponse)
async def set_accordion_preset(request: Request, category: str, preset: str, filename: str = Form("")):
    """Update a category's preset and return updated accordion."""
    if category not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_category_preset(category, preset, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    # Return correct template based on category type
    if category in VIDEO_CATEGORIES:
        return templates.TemplateResponse("partials/effects_video_accordion.html", context)
    return templates.TemplateResponse("partials/effects_audio_accordion.html", context)
