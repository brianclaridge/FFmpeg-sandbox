"""Audio processing router."""

from pathlib import Path

import subprocess
import tempfile
import os

import json

from fastapi import APIRouter, Form, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

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
    get_presets_by_preset_category,
    reload_presets,
)
from app.services.user_shortcuts import (
    save_user_shortcut,
    delete_user_shortcut,
    export_shortcuts,
    import_shortcuts,
    generate_shortcut_key,
)
from app.services.presets_themes import (
    get_video_theme_presets,
    get_audio_theme_presets,
    get_theme_preset,
)
from app.services.settings import (
    load_user_settings,
    update_category_preset,
    update_category_custom_values,
    update_active_category,
    update_active_tab,
    toggle_theme_preset,
    get_current_theme_chain,
)
from app.services import (
    process_audio,
    process_audio_with_filters,
    process_video_with_filters,
    get_input_files,
    get_file_duration,
    format_duration_ms,
    get_file_metadata,
    build_audio_filter_chain,
    build_video_filter_chain,
)
from app.services.processor import process_video_with_progress
from app.services.file_metadata import load_file_metadata
from app.services.history import add_history_entry

ALLOWED_EXTENSIONS = set(config.audio.allowed_extensions)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


AUDIO_FORMATS = {"mp3", "wav", "flac"}
VIDEO_FORMATS = {"mp4", "webm", "mkv"}


@router.post("/process", response_class=HTMLResponse)
async def process(
    request: Request,
    input_file: str = Form(...),
    start_time: str = Form(config.audio.default_start_time),
    end_time: str = Form(config.audio.default_end_time),
    output_format: str = Form("mp3"),
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

    # Video filter presets
    brightness_config = brightness_presets.get(user_settings.brightness.preset) or brightness_presets["none"]
    contrast_config = contrast_presets.get(user_settings.contrast.preset) or contrast_presets["none"]
    saturation_config = saturation_presets.get(user_settings.saturation.preset) or saturation_presets["none"]
    blur_config = blur_presets.get(user_settings.blur.preset) or blur_presets["none"]
    sharpen_config = sharpen_presets.get(user_settings.sharpen.preset) or sharpen_presets["none"]
    transform_config = transform_presets.get(user_settings.transform.preset) or transform_presets["none"]

    # Extract actual filter values - check custom_values first (for theme presets)
    # Audio filters
    volume_val = (user_settings.volume.custom_values.get("volume", volume_config.volume)
                  if user_settings.volume.custom_values else volume_config.volume)
    highpass_val = (user_settings.frequency.custom_values.get("highpass", frequency_config.highpass)
                    if user_settings.frequency.custom_values else frequency_config.highpass)
    lowpass_val = (user_settings.frequency.custom_values.get("lowpass", frequency_config.lowpass)
                   if user_settings.frequency.custom_values else frequency_config.lowpass)
    delays_list = (user_settings.tunnel.custom_values.get("delays", tunnel_config.delays)
                   if user_settings.tunnel.custom_values else tunnel_config.delays)
    decays_list = (user_settings.tunnel.custom_values.get("decays", tunnel_config.decays)
                   if user_settings.tunnel.custom_values else tunnel_config.decays)
    speed_val = (user_settings.speed.custom_values.get("speed", speed_config.speed)
                 if user_settings.speed.custom_values else speed_config.speed)
    pitch_val = (user_settings.pitch.custom_values.get("semitones", pitch_config.semitones)
                 if user_settings.pitch.custom_values else pitch_config.semitones)
    noise_floor_val = (user_settings.noise_reduction.custom_values.get("noise_floor", noise_config.noise_floor)
                       if user_settings.noise_reduction.custom_values else noise_config.noise_floor)
    noise_reduction_val = (user_settings.noise_reduction.custom_values.get("noise_reduction", noise_config.noise_reduction)
                           if user_settings.noise_reduction.custom_values else noise_config.noise_reduction)
    comp_threshold_val = (user_settings.compressor.custom_values.get("threshold", comp_config.threshold)
                          if user_settings.compressor.custom_values else comp_config.threshold)
    comp_ratio_val = (user_settings.compressor.custom_values.get("ratio", comp_config.ratio)
                      if user_settings.compressor.custom_values else comp_config.ratio)
    comp_attack_val = (user_settings.compressor.custom_values.get("attack", comp_config.attack)
                       if user_settings.compressor.custom_values else comp_config.attack)
    comp_release_val = (user_settings.compressor.custom_values.get("release", comp_config.release)
                        if user_settings.compressor.custom_values else comp_config.release)
    comp_makeup_val = (user_settings.compressor.custom_values.get("makeup", comp_config.makeup)
                       if user_settings.compressor.custom_values else comp_config.makeup)

    # Video filters
    brightness_val = (user_settings.brightness.custom_values.get("brightness", brightness_config.brightness)
                      if user_settings.brightness.custom_values else brightness_config.brightness)
    contrast_val = (user_settings.contrast.custom_values.get("contrast", contrast_config.contrast)
                    if user_settings.contrast.custom_values else contrast_config.contrast)
    saturation_val = (user_settings.saturation.custom_values.get("saturation", saturation_config.saturation)
                      if user_settings.saturation.custom_values else saturation_config.saturation)
    blur_sigma_val = (user_settings.blur.custom_values.get("sigma", blur_config.sigma)
                      if user_settings.blur.custom_values else blur_config.sigma)
    sharpen_amount_val = (user_settings.sharpen.custom_values.get("amount", sharpen_config.amount)
                          if user_settings.sharpen.custom_values else sharpen_config.amount)
    transform_val = (user_settings.transform.custom_values.get("filter", transform_config.filter)
                     if user_settings.transform.custom_values else transform_config.filter)

    # Theme-only video filters (crop, colorshift, overlay, scale)
    crop_val = (user_settings.crop.custom_values.get("aspect_ratio", "")
                if user_settings.crop.custom_values else "")
    colorshift_val = (user_settings.colorshift.custom_values.get("shift_amount", 0)
                      if user_settings.colorshift.custom_values else 0)
    overlay_val = (user_settings.overlay.custom_values.get("overlay_type", "")
                   if user_settings.overlay.custom_values else "")
    scale_width_val = (user_settings.scale.custom_values.get("width", 0)
                       if user_settings.scale.custom_values else 0)
    scale_height_val = (user_settings.scale.custom_values.get("height", 0)
                        if user_settings.scale.custom_values else 0)

    # Build audio filter chain with all filters (speed is linked)
    delays_str = "|".join(str(d) for d in delays_list)
    decays_str = "|".join(str(d) for d in decays_list)

    audio_filter = build_audio_filter_chain(
        volume=volume_val,
        highpass=highpass_val,
        lowpass=lowpass_val,
        delays=delays_str,
        decays=decays_str,
        speed=speed_val,
        pitch_semitones=pitch_val,
        noise_floor=noise_floor_val,
        noise_reduction=noise_reduction_val,
        comp_threshold=comp_threshold_val,
        comp_ratio=comp_ratio_val,
        comp_attack=comp_attack_val,
        comp_release=comp_release_val,
        comp_makeup=comp_makeup_val,
    )

    # Check if input is a video file
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
    is_video = input_path.suffix.lower() in video_extensions

    # Check if any video filters are active
    video_filters_active = (
        brightness_val != 0.0 or
        contrast_val != 1.0 or
        saturation_val != 1.0 or
        blur_sigma_val > 0 or
        sharpen_amount_val > 0 or
        transform_val != "" or
        speed_val != 1.0 or  # Speed affects video PTS too
        crop_val != "" or
        colorshift_val > 0 or
        overlay_val != "" or
        scale_width_val > 0 or
        scale_height_val > 0
    )

    try:
        # Determine output type based on user-selected format
        wants_video_output = output_format in VIDEO_FORMATS

        # Validate format: can only output video if input is video
        if wants_video_output and not is_video:
            # Input is audio-only, fall back to audio format
            output_format = "mp3"
            wants_video_output = False

        # If audio format selected but no valid audio format, use mp3
        if not wants_video_output and output_format not in AUDIO_FORMATS:
            output_format = "mp3"

        if wants_video_output and is_video:
            # Build video filter chain (with same speed for sync)
            video_filter = build_video_filter_chain(
                brightness=brightness_val,
                contrast=contrast_val,
                saturation=saturation_val,
                blur_sigma=blur_sigma_val,
                sharpen_amount=sharpen_amount_val,
                transform=transform_val,
                speed=speed_val,
                crop_aspect=crop_val,
                colorshift=colorshift_val,
                overlay=overlay_val,
                scale_width=scale_width_val,
                scale_height=scale_height_val,
            )

            output_path = process_video_with_filters(
                input_file=input_path,
                start_time=start_time,
                end_time=end_time,
                audio_filter=audio_filter,
                video_filter=video_filter,
                output_format=output_format,
            )
        else:
            # Audio-only output with full filter chain (all 7 audio filters)
            output_path = process_audio_with_filters(
                input_file=input_path,
                start_time=start_time,
                end_time=end_time,
                audio_filter=audio_filter,
                output_format=output_format,
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
                "output_format": output_format.upper(),
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
    """Extract audio from video without applying filters."""
    input_path = INPUT_DIR / input_file

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found")

    try:
        # Extract audio with neutral settings (no filters)
        output_path = process_audio(
            input_file=input_path,
            start_time=start_time,
            end_time=end_time,
            volume=1.0,        # No volume change
            highpass=20,       # Minimal high-pass (full bass)
            lowpass=20000,     # Minimal low-pass (full treble)
            delays="1",        # Minimal delay
            decays="0",        # No echo
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

    # Get current shortcut configs for each category (with fallbacks)
    volume_current = volume_shortcuts.get(user_settings.volume.preset) or volume_shortcuts["none"]
    tunnel_current = tunnel_shortcuts.get(user_settings.tunnel.preset) or tunnel_shortcuts["none"]
    frequency_current = frequency_shortcuts.get(user_settings.frequency.preset) or frequency_shortcuts["none"]
    speed_current = speed_shortcuts.get(user_settings.speed.preset) or speed_shortcuts["none"]
    pitch_current = pitch_shortcuts.get(user_settings.pitch.preset) or pitch_shortcuts["none"]
    noise_reduction_current = noise_reduction_shortcuts.get(user_settings.noise_reduction.preset) or noise_reduction_shortcuts["none"]
    compressor_current = compressor_shortcuts.get(user_settings.compressor.preset) or compressor_shortcuts["none"]

    # Video filters
    brightness_current = brightness_shortcuts.get(user_settings.brightness.preset) or brightness_shortcuts["none"]
    contrast_current = contrast_shortcuts.get(user_settings.contrast.preset) or contrast_shortcuts["none"]
    saturation_current = saturation_shortcuts.get(user_settings.saturation.preset) or saturation_shortcuts["none"]
    blur_current = blur_shortcuts.get(user_settings.blur.preset) or blur_shortcuts["none"]
    sharpen_current = sharpen_shortcuts.get(user_settings.sharpen.preset) or sharpen_shortcuts["none"]
    transform_current = transform_shortcuts.get(user_settings.transform.preset) or transform_shortcuts["none"]

    return {
        "user_settings": user_settings,
        # Audio shortcuts
        "volume_shortcuts": volume_shortcuts,
        "tunnel_shortcuts": tunnel_shortcuts,
        "frequency_shortcuts": frequency_shortcuts,
        "speed_shortcuts": speed_shortcuts,
        "pitch_shortcuts": pitch_shortcuts,
        "noise_reduction_shortcuts": noise_reduction_shortcuts,
        "compressor_shortcuts": compressor_shortcuts,
        # Video shortcuts
        "brightness_shortcuts": brightness_shortcuts,
        "contrast_shortcuts": contrast_shortcuts,
        "saturation_shortcuts": saturation_shortcuts,
        "blur_shortcuts": blur_shortcuts,
        "sharpen_shortcuts": sharpen_shortcuts,
        "transform_shortcuts": transform_shortcuts,
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


@router.get("/partials/filter-chain", response_class=HTMLResponse)
async def get_filter_chain(request: Request, filename: str | None = None):
    """Get the full filter chain UI component (tabs with accordion)."""
    user_settings = load_user_settings(filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    # Add theme presets if on presets tab
    if user_settings.active_tab == "presets":
        context["video_theme_presets"] = get_video_theme_presets()
        context["audio_theme_presets"] = get_audio_theme_presets()

    return templates.TemplateResponse("partials/filters_tabs.html", context)


@router.get("/partials/filters-tab/{tab}", response_class=HTMLResponse)
async def get_filters_tab(request: Request, tab: str, filename: str | None = None):
    """Switch between Audio, Video, and Presets tabs."""
    if tab not in ("audio", "video", "presets"):
        raise HTTPException(status_code=404, detail="Tab not found")

    user_settings = update_active_tab(tab, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    # Add theme presets for presets tab
    if tab == "presets":
        context["video_theme_presets"] = get_video_theme_presets()
        context["audio_theme_presets"] = get_audio_theme_presets()

    # Return full tabs container so tab buttons update their active state
    return templates.TemplateResponse("partials/filters_tabs.html", context)


AUDIO_CATEGORIES = ("volume", "tunnel", "frequency", "speed", "pitch", "noise_reduction", "compressor")
VIDEO_CATEGORIES = ("brightness", "contrast", "saturation", "blur", "sharpen", "transform", "crop", "colorshift", "overlay", "scale")
ALL_CATEGORIES = AUDIO_CATEGORIES + VIDEO_CATEGORIES


@router.get("/partials/category-panel/{category}", response_class=HTMLResponse)
async def get_category_panel(request: Request, category: str, filename: str | None = None):
    """Get the control panel for a specific category (legacy endpoint - returns accordion)."""
    if category not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/filters_audio_accordion.html", context)


@router.post("/partials/category-preset/{category}/{preset}", response_class=HTMLResponse)
async def set_category_preset(request: Request, category: str, preset: str, filename: str = Form("")):
    """Update a category's preset selection (legacy endpoint - redirects to accordion)."""
    user_settings = update_category_preset(category, preset, filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    return templates.TemplateResponse("partials/filters_audio_accordion.html", context)


@router.get("/partials/accordion/{category}", response_class=HTMLResponse)
async def get_accordion_section(
    request: Request,
    category: str,
    filename: str | None = None,
    current_category: str | None = None,
):
    """Expand an accordion section (collapses others)."""
    if category not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename, current_category)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request

    # Return correct template based on category type
    if category in VIDEO_CATEGORIES:
        return templates.TemplateResponse("partials/filters_video_accordion.html", context)
    return templates.TemplateResponse("partials/filters_audio_accordion.html", context)


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
        return templates.TemplateResponse("partials/filters_video_accordion.html", context)
    return templates.TemplateResponse("partials/filters_audio_accordion.html", context)


# ============ PRESET MANAGEMENT ENDPOINTS ============

@router.get("/partials/save-shortcut-modal/{filter_type}/{category}", response_class=HTMLResponse)
async def get_save_shortcut_modal(
    request: Request,
    filter_type: str,
    category: str,
    filename: str | None = None,
):
    """Return the save preset modal HTML."""
    if filter_type not in ("audio", "video"):
        raise HTTPException(status_code=400, detail="Invalid filter type")

    valid_categories = AUDIO_CATEGORIES if filter_type == "audio" else VIDEO_CATEGORIES
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")

    # Get current slider values from user settings
    user_settings = load_user_settings(filename)
    current_preset_key = getattr(user_settings, category).preset

    # Get the current config values for default population
    preset_getters = {
        "volume": get_volume_presets,
        "tunnel": get_tunnel_presets,
        "frequency": get_frequency_presets,
        "speed": get_speed_presets,
        "pitch": get_pitch_presets,
        "noise_reduction": get_noise_reduction_presets,
        "compressor": get_compressor_presets,
        "brightness": get_brightness_presets,
        "contrast": get_contrast_presets,
        "saturation": get_saturation_presets,
        "blur": get_blur_presets,
        "sharpen": get_sharpen_presets,
        "transform": get_transform_presets,
    }

    presets = preset_getters[category]()
    current_config = presets.get(current_preset_key) or presets.get("none")

    return templates.TemplateResponse(
        "partials/save_shortcut_modal.html",
        {
            "request": request,
            "filter_type": filter_type,
            "category": category,
            "current_config": current_config,
            "current_filename": filename,
        },
    )


@router.post("/shortcuts/save", response_class=HTMLResponse)
async def save_shortcut(
    request: Request,
    filter_type: str = Form(...),
    category: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    preset_category: str = Form("Custom"),
    filename: str = Form(""),
    # Audio filter fields
    volume: float | None = Form(None),
    highpass: int | None = Form(None),
    lowpass: int | None = Form(None),
    delays: str | None = Form(None),
    decays: str | None = Form(None),
    speed: float | None = Form(None),
    semitones: float | None = Form(None),
    noise_floor: float | None = Form(None),
    noise_reduction: float | None = Form(None),
    threshold: float | None = Form(None),
    ratio: float | None = Form(None),
    attack: float | None = Form(None),
    release: float | None = Form(None),
    makeup: float | None = Form(None),
    # Video filter fields
    brightness: float | None = Form(None),
    contrast: float | None = Form(None),
    saturation: float | None = Form(None),
    sigma: float | None = Form(None),
    amount: float | None = Form(None),
    filter_value: str | None = Form(None, alias="filter"),
):
    """Save a new user preset from form data."""
    if filter_type not in ("audio", "video"):
        raise HTTPException(status_code=400, detail="Invalid filter type")

    valid_categories = AUDIO_CATEGORIES if filter_type == "audio" else VIDEO_CATEGORIES
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")

    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Preset name is required")

    preset_key = generate_shortcut_key(name)

    # Build preset data based on category
    preset_data = {
        "name": name.strip(),
        "description": description.strip() if description else f"Custom {category} preset",
        "preset_category": preset_category,
    }

    # Add category-specific fields
    if category == "volume" and volume is not None:
        preset_data["volume"] = volume
    elif category == "tunnel" and delays is not None and decays is not None:
        preset_data["delays"] = [int(d) for d in delays.split("|") if d]
        preset_data["decays"] = [float(d) for d in decays.split("|") if d]
    elif category == "frequency" and highpass is not None and lowpass is not None:
        preset_data["highpass"] = highpass
        preset_data["lowpass"] = lowpass
    elif category == "speed" and speed is not None:
        preset_data["speed"] = speed
    elif category == "pitch" and semitones is not None:
        preset_data["semitones"] = semitones
    elif category == "noise_reduction" and noise_floor is not None and noise_reduction is not None:
        preset_data["noise_floor"] = noise_floor
        preset_data["noise_reduction"] = noise_reduction
    elif category == "compressor":
        if all(v is not None for v in [threshold, ratio, attack, release, makeup]):
            preset_data["threshold"] = threshold
            preset_data["ratio"] = ratio
            preset_data["attack"] = attack
            preset_data["release"] = release
            preset_data["makeup"] = makeup
    elif category == "brightness" and brightness is not None:
        preset_data["brightness"] = brightness
    elif category == "contrast" and contrast is not None:
        preset_data["contrast"] = contrast
    elif category == "saturation" and saturation is not None:
        preset_data["saturation"] = saturation
    elif category == "blur" and sigma is not None:
        preset_data["sigma"] = sigma
    elif category == "sharpen" and amount is not None:
        preset_data["amount"] = amount
    elif category == "transform" and filter_value is not None:
        preset_data["filter"] = filter_value

    success = save_user_shortcut(filter_type, category, preset_key, preset_data)

    if success:
        reload_presets()
        user_settings = update_category_preset(category, preset_key, filename)
        context = _get_accordion_context(user_settings, filename)
        context["request"] = request
        context["save_success"] = True
        context["saved_preset_name"] = name.strip()

        if filter_type == "video":
            return templates.TemplateResponse("partials/filters_video_accordion.html", context)
        return templates.TemplateResponse("partials/filters_audio_accordion.html", context)
    else:
        raise HTTPException(status_code=500, detail="Failed to save preset")


@router.delete("/shortcuts/{filter_type}/{category}/{shortcut_key}", response_class=HTMLResponse)
async def delete_shortcut(
    request: Request,
    filter_type: str,
    category: str,
    preset_key: str,
    filename: str | None = None,
):
    """Delete a user preset."""
    if filter_type not in ("audio", "video"):
        raise HTTPException(status_code=400, detail="Invalid filter type")

    valid_categories = AUDIO_CATEGORIES if filter_type == "audio" else VIDEO_CATEGORIES
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")

    success = delete_user_shortcut(filter_type, category, preset_key)

    if success:
        reload_presets()
        # Reset to "none" preset after deletion
        user_settings = update_category_preset(category, "none", filename)
        context = _get_accordion_context(user_settings, filename)
        context["request"] = request
        context["delete_success"] = True

        if filter_type == "video":
            return templates.TemplateResponse("partials/filters_video_accordion.html", context)
        return templates.TemplateResponse("partials/filters_audio_accordion.html", context)
    else:
        raise HTTPException(status_code=404, detail="Preset not found")


@router.get("/shortcuts/export")
async def export_shortcuts_endpoint(
    filter_type: str | None = None,
    category: str | None = None,
    include_system: bool = False,
):
    """Export presets as YAML file download."""
    yaml_content = export_shortcuts(
        filter_type=filter_type,
        filter_category=category,
        include_system=include_system,
    )

    # Generate filename
    if filter_type and category:
        filename = f"{filter_type}_{category}_presets.yml"
    elif filter_type:
        filename = f"{filter_type}_presets.yml"
    else:
        filename = "user_presets.yml" if not include_system else "all_presets.yml"

    return StreamingResponse(
        iter([yaml_content]),
        media_type="application/x-yaml",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/shortcuts/import", response_class=HTMLResponse)
async def import_shortcuts_endpoint(
    request: Request,
    file: UploadFile = File(...),
    merge: bool = Form(True),
    filename: str = Form(""),
):
    """Import presets from uploaded YAML file."""
    if not file.filename or not file.filename.endswith((".yml", ".yaml")):
        return templates.TemplateResponse(
            "partials/import_result.html",
            {
                "request": request,
                "success": False,
                "error": "Please upload a .yml or .yaml file",
            },
        )

    try:
        content = await file.read()
        yaml_content = content.decode("utf-8")
    except Exception as e:
        return templates.TemplateResponse(
            "partials/import_result.html",
            {
                "request": request,
                "success": False,
                "error": f"Failed to read file: {e}",
            },
        )

    result = import_shortcuts(yaml_content, merge=merge)

    if result["errors"]:
        return templates.TemplateResponse(
            "partials/import_result.html",
            {
                "request": request,
                "success": False,
                "error": "; ".join(result["errors"][:3]),
                "result": result,
            },
        )

    reload_presets()
    user_settings = load_user_settings(filename)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    context["import_success"] = True
    context["import_result"] = result

    return templates.TemplateResponse(
        "partials/import_result.html",
        {
            "request": request,
            "success": True,
            "result": result,
        },
    )


# ============ THEME PRESET ENDPOINTS ============

THEME_PRESET_CATEGORIES = ("video_presets", "audio_presets")


@router.get("/partials/presets-accordion/{category}", response_class=HTMLResponse)
async def get_presets_accordion_section(
    request: Request,
    category: str,
    filename: str | None = None,
    current_category: str | None = None,
):
    """Expand a presets accordion section."""
    if category not in THEME_PRESET_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    user_settings = update_active_category(category, filename, current_category)
    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    context["video_theme_presets"] = get_video_theme_presets()
    context["audio_theme_presets"] = get_audio_theme_presets()
    context["video_theme_chain"] = user_settings.video_theme_chain
    context["audio_theme_chain"] = user_settings.audio_theme_chain

    return templates.TemplateResponse("partials/filters_presets_accordion.html", context)


@router.post("/toggle-theme-preset/{media_type}/{preset_key}", response_class=HTMLResponse)
async def toggle_theme_preset_endpoint(
    request: Request,
    media_type: str,
    preset_key: str,
    filename: str = Form(""),
):
    """Toggle a theme preset in the chain.

    If preset is in chain, remove it. If not, add to end.
    If preset_key is "none", clear the entire chain.
    All presets in chain are applied in order (last wins for conflicts).
    """
    if media_type not in ("audio", "video"):
        raise HTTPException(status_code=400, detail="Invalid media type")

    # Determine which categories to affect based on media type
    categories_to_clear = VIDEO_CATEGORIES if media_type == "video" else AUDIO_CATEGORIES

    # Toggle the preset in chain (or clear if "none")
    user_settings, chain = toggle_theme_preset(media_type, preset_key, filename)

    # Clear existing custom values for this media type's categories
    for category in categories_to_clear:
        update_category_preset(category, "none", filename)

    # Apply all presets in chain order (last wins for conflicts)
    applied_preset_name = None
    for chain_preset_key in chain:
        preset = get_theme_preset(media_type, chain_preset_key)
        if preset:
            for filter_step in preset.filters:
                filter_type = filter_step.type
                if filter_type in ALL_CATEGORIES:
                    update_category_custom_values(filter_type, filter_step.params, filename)
            applied_preset_name = preset.name

    # Reload settings after applying all filters
    user_settings = load_user_settings(filename)

    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    context["video_theme_presets"] = get_video_theme_presets()
    context["audio_theme_presets"] = get_audio_theme_presets()
    context["video_theme_chain"] = user_settings.video_theme_chain
    context["audio_theme_chain"] = user_settings.audio_theme_chain

    if chain and applied_preset_name:
        context["apply_success"] = True
        context["applied_preset_name"] = applied_preset_name
        context["chain_count"] = len(chain)

    return templates.TemplateResponse("partials/filters_presets_accordion.html", context)


# ============ PROGRESS STREAMING ENDPOINT ============

def _parse_time_to_ms(time_str: str) -> int:
    """Convert HH:MM:SS or HH:MM:SS.mmm to milliseconds."""
    parts = time_str.split(":")
    if len(parts) != 3:
        return 0
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split(".")
    seconds = int(seconds_parts[0])
    ms = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + ms


@router.get("/process-with-progress")
async def process_with_progress(
    request: Request,
    input_file: str,
    start_time: str = "00:00:00",
    end_time: str = "00:00:06",
    output_format: str = "mp4",
):
    """Process video with SSE progress streaming."""
    input_path = INPUT_DIR / input_file

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found")

    # Load user settings
    user_settings = load_user_settings(input_file)

    # Get preset dictionaries (abbreviated - only what's needed)
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

    # Get configs
    volume_config = volume_presets.get(user_settings.volume.preset) or volume_presets["none"]
    tunnel_config = tunnel_presets.get(user_settings.tunnel.preset) or tunnel_presets["none"]
    frequency_config = frequency_presets.get(user_settings.frequency.preset) or frequency_presets["none"]
    speed_config = speed_presets.get(user_settings.speed.preset) or speed_presets["none"]
    pitch_config = pitch_presets.get(user_settings.pitch.preset) or pitch_presets["none"]
    noise_config = noise_presets.get(user_settings.noise_reduction.preset) or noise_presets["none"]
    comp_config = compressor_presets.get(user_settings.compressor.preset) or compressor_presets["none"]
    brightness_config = brightness_presets.get(user_settings.brightness.preset) or brightness_presets["none"]
    contrast_config = contrast_presets.get(user_settings.contrast.preset) or contrast_presets["none"]
    saturation_config = saturation_presets.get(user_settings.saturation.preset) or saturation_presets["none"]
    blur_config = blur_presets.get(user_settings.blur.preset) or blur_presets["none"]
    sharpen_config = sharpen_presets.get(user_settings.sharpen.preset) or sharpen_presets["none"]
    transform_config = transform_presets.get(user_settings.transform.preset) or transform_presets["none"]

    # Extract values (simplified - uses custom_values if present)
    volume_val = user_settings.volume.custom_values.get("volume", volume_config.volume) if user_settings.volume.custom_values else volume_config.volume
    highpass_val = user_settings.frequency.custom_values.get("highpass", frequency_config.highpass) if user_settings.frequency.custom_values else frequency_config.highpass
    lowpass_val = user_settings.frequency.custom_values.get("lowpass", frequency_config.lowpass) if user_settings.frequency.custom_values else frequency_config.lowpass
    delays_list = user_settings.tunnel.custom_values.get("delays", tunnel_config.delays) if user_settings.tunnel.custom_values else tunnel_config.delays
    decays_list = user_settings.tunnel.custom_values.get("decays", tunnel_config.decays) if user_settings.tunnel.custom_values else tunnel_config.decays
    speed_val = user_settings.speed.custom_values.get("speed", speed_config.speed) if user_settings.speed.custom_values else speed_config.speed
    pitch_val = user_settings.pitch.custom_values.get("semitones", pitch_config.semitones) if user_settings.pitch.custom_values else pitch_config.semitones
    noise_floor_val = user_settings.noise_reduction.custom_values.get("noise_floor", noise_config.noise_floor) if user_settings.noise_reduction.custom_values else noise_config.noise_floor
    noise_reduction_val = user_settings.noise_reduction.custom_values.get("noise_reduction", noise_config.noise_reduction) if user_settings.noise_reduction.custom_values else noise_config.noise_reduction
    comp_threshold_val = user_settings.compressor.custom_values.get("threshold", comp_config.threshold) if user_settings.compressor.custom_values else comp_config.threshold
    comp_ratio_val = user_settings.compressor.custom_values.get("ratio", comp_config.ratio) if user_settings.compressor.custom_values else comp_config.ratio
    comp_attack_val = user_settings.compressor.custom_values.get("attack", comp_config.attack) if user_settings.compressor.custom_values else comp_config.attack
    comp_release_val = user_settings.compressor.custom_values.get("release", comp_config.release) if user_settings.compressor.custom_values else comp_config.release
    comp_makeup_val = user_settings.compressor.custom_values.get("makeup", comp_config.makeup) if user_settings.compressor.custom_values else comp_config.makeup

    # Video filters
    brightness_val = user_settings.brightness.custom_values.get("brightness", brightness_config.brightness) if user_settings.brightness.custom_values else brightness_config.brightness
    contrast_val = user_settings.contrast.custom_values.get("contrast", contrast_config.contrast) if user_settings.contrast.custom_values else contrast_config.contrast
    saturation_val = user_settings.saturation.custom_values.get("saturation", saturation_config.saturation) if user_settings.saturation.custom_values else saturation_config.saturation
    blur_sigma_val = user_settings.blur.custom_values.get("sigma", blur_config.sigma) if user_settings.blur.custom_values else blur_config.sigma
    sharpen_amount_val = user_settings.sharpen.custom_values.get("amount", sharpen_config.amount) if user_settings.sharpen.custom_values else sharpen_config.amount
    transform_val = user_settings.transform.custom_values.get("filter", transform_config.filter) if user_settings.transform.custom_values else transform_config.filter

    # Theme-only filters
    crop_val = user_settings.crop.custom_values.get("aspect_ratio", "") if user_settings.crop.custom_values else ""
    colorshift_val = user_settings.colorshift.custom_values.get("shift_amount", 0) if user_settings.colorshift.custom_values else 0
    overlay_val = user_settings.overlay.custom_values.get("overlay_type", "") if user_settings.overlay.custom_values else ""
    scale_width_val = user_settings.scale.custom_values.get("width", 0) if user_settings.scale.custom_values else 0
    scale_height_val = user_settings.scale.custom_values.get("height", 0) if user_settings.scale.custom_values else 0

    # Build filter chains
    delays_str = "|".join(str(d) for d in delays_list)
    decays_str = "|".join(str(d) for d in decays_list)

    audio_filter = build_audio_filter_chain(
        volume=volume_val,
        highpass=highpass_val,
        lowpass=lowpass_val,
        delays=delays_str,
        decays=decays_str,
        speed=speed_val,
        pitch_semitones=pitch_val,
        noise_floor=noise_floor_val,
        noise_reduction=noise_reduction_val,
        comp_threshold=comp_threshold_val,
        comp_ratio=comp_ratio_val,
        comp_attack=comp_attack_val,
        comp_release=comp_release_val,
        comp_makeup=comp_makeup_val,
    )

    video_filter = build_video_filter_chain(
        brightness=brightness_val,
        contrast=contrast_val,
        saturation=saturation_val,
        blur_sigma=blur_sigma_val,
        sharpen_amount=sharpen_amount_val,
        transform=transform_val,
        speed=speed_val,
        crop_aspect=crop_val,
        colorshift=colorshift_val,
        overlay=overlay_val,
        scale_width=scale_width_val,
        scale_height=scale_height_val,
    )

    # Calculate total duration in ms
    start_ms = _parse_time_to_ms(start_time)
    end_ms = _parse_time_to_ms(end_time)
    total_duration_ms = end_ms - start_ms

    async def event_generator():
        """Generate SSE events from processor."""
        output_file = None
        try:
            for update in process_video_with_progress(
                input_file=input_path,
                start_time=start_time,
                end_time=end_time,
                audio_filter=audio_filter,
                video_filter=video_filter,
                output_format=output_format,
                total_duration_ms=total_duration_ms,
            ):
                yield {
                    "event": update["type"],
                    "data": json.dumps(update),
                }
                if update["type"] == "complete":
                    output_file = update.get("output_file")

            # Add history entry on success
            if output_file:
                add_history_entry(
                    input_file=input_file,
                    output_file=output_file,
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

        except Exception as e:
            logger.exception("Processing with progress failed")
            yield {
                "event": "error",
                "data": json.dumps({"type": "error", "message": str(e)}),
            }

    return EventSourceResponse(event_generator())
