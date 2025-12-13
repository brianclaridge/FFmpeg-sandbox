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
    # Audio effects
    VolumePreset, VOLUME_PRESETS, VOLUME_PRESETS_BY_STR,
    TunnelPreset, TUNNEL_PRESETS, TUNNEL_PRESETS_BY_STR,
    FrequencyPreset, FREQUENCY_PRESETS, FREQUENCY_PRESETS_BY_STR,
    SpeedPreset, SPEED_PRESETS, SPEED_PRESETS_BY_STR,
    PitchPreset, PITCH_PRESETS, PITCH_PRESETS_BY_STR,
    NoiseReductionPreset, NOISE_REDUCTION_PRESETS, NOISE_REDUCTION_PRESETS_BY_STR,
    CompressorPreset, COMPRESSOR_PRESETS, COMPRESSOR_PRESETS_BY_STR,
    # Video effects
    BrightnessPreset, BRIGHTNESS_PRESETS, BRIGHTNESS_PRESETS_BY_STR,
    ContrastPreset, CONTRAST_PRESETS, CONTRAST_PRESETS_BY_STR,
    SaturationPreset, SATURATION_PRESETS, SATURATION_PRESETS_BY_STR,
    BlurPreset, BLUR_PRESETS, BLUR_PRESETS_BY_STR,
    SharpenPreset, SHARPEN_PRESETS, SHARPEN_PRESETS_BY_STR,
    TransformPreset, TRANSFORM_PRESETS, TRANSFORM_PRESETS_BY_STR,
)
from app.services.settings import (
    load_user_settings,
    update_category_preset,
    update_active_category,
    update_active_tab,
)
from app.services.processor import (
    process_audio,
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

    # Lookup all preset configurations from user settings
    try:
        volume_config = VOLUME_PRESETS[VolumePreset(user_settings.volume.preset)]
    except (ValueError, KeyError):
        volume_config = VOLUME_PRESETS[VolumePreset.X2]

    try:
        tunnel_config = TUNNEL_PRESETS[TunnelPreset(user_settings.tunnel.preset)]
    except (ValueError, KeyError):
        tunnel_config = TUNNEL_PRESETS[TunnelPreset.NONE]

    try:
        frequency_config = FREQUENCY_PRESETS[FrequencyPreset(user_settings.frequency.preset)]
    except (ValueError, KeyError):
        frequency_config = FREQUENCY_PRESETS[FrequencyPreset.FLAT]

    try:
        speed_config = SPEED_PRESETS[SpeedPreset(user_settings.speed.preset)]
    except (ValueError, KeyError):
        speed_config = SPEED_PRESETS[SpeedPreset.NONE]

    try:
        pitch_config = PITCH_PRESETS[PitchPreset(user_settings.pitch.preset)]
    except (ValueError, KeyError):
        pitch_config = PITCH_PRESETS[PitchPreset.NONE]

    try:
        noise_config = NOISE_REDUCTION_PRESETS[NoiseReductionPreset(user_settings.noise_reduction.preset)]
    except (ValueError, KeyError):
        noise_config = NOISE_REDUCTION_PRESETS[NoiseReductionPreset.NONE]

    try:
        comp_config = COMPRESSOR_PRESETS[CompressorPreset(user_settings.compressor.preset)]
    except (ValueError, KeyError):
        comp_config = COMPRESSOR_PRESETS[CompressorPreset.NONE]

    # Video effect presets
    try:
        brightness_config = BRIGHTNESS_PRESETS[BrightnessPreset(user_settings.brightness.preset)]
    except (ValueError, KeyError):
        brightness_config = BRIGHTNESS_PRESETS[BrightnessPreset.NONE]

    try:
        contrast_config = CONTRAST_PRESETS[ContrastPreset(user_settings.contrast.preset)]
    except (ValueError, KeyError):
        contrast_config = CONTRAST_PRESETS[ContrastPreset.NONE]

    try:
        saturation_config = SATURATION_PRESETS[SaturationPreset(user_settings.saturation.preset)]
    except (ValueError, KeyError):
        saturation_config = SATURATION_PRESETS[SaturationPreset.NONE]

    try:
        blur_config = BLUR_PRESETS[BlurPreset(user_settings.blur.preset)]
    except (ValueError, KeyError):
        blur_config = BLUR_PRESETS[BlurPreset.NONE]

    try:
        sharpen_config = SHARPEN_PRESETS[SharpenPreset(user_settings.sharpen.preset)]
    except (ValueError, KeyError):
        sharpen_config = SHARPEN_PRESETS[SharpenPreset.NONE]

    try:
        transform_config = TRANSFORM_PRESETS[TransformPreset(user_settings.transform.preset)]
    except (ValueError, KeyError):
        transform_config = TRANSFORM_PRESETS[TransformPreset.NONE]

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
            # Audio-only extraction (uses legacy process_audio for MP3 output)
            output_path = process_audio(
                input_file=input_path,
                start_time=start_time,
                end_time=end_time,
                volume=volume_config.volume,
                highpass=frequency_config.highpass,
                lowpass=frequency_config.lowpass,
                delays=delays_str,
                decays=decays_str,
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
            volume_preset="1x",
            tunnel_preset="none",
            frequency_preset="flat",
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
    # Get current preset configs for each category
    try:
        volume_current = VOLUME_PRESETS[VolumePreset(user_settings.volume.preset)]
    except (ValueError, KeyError):
        volume_current = VOLUME_PRESETS[VolumePreset("none")]

    try:
        tunnel_current = TUNNEL_PRESETS[TunnelPreset(user_settings.tunnel.preset)]
    except (ValueError, KeyError):
        tunnel_current = TUNNEL_PRESETS[TunnelPreset("none")]

    try:
        frequency_current = FREQUENCY_PRESETS[FrequencyPreset(user_settings.frequency.preset)]
    except (ValueError, KeyError):
        frequency_current = FREQUENCY_PRESETS[FrequencyPreset("flat")]

    try:
        speed_current = SPEED_PRESETS[SpeedPreset(user_settings.speed.preset)]
    except (ValueError, KeyError):
        speed_current = SPEED_PRESETS[SpeedPreset("none")]

    try:
        pitch_current = PITCH_PRESETS[PitchPreset(user_settings.pitch.preset)]
    except (ValueError, KeyError):
        pitch_current = PITCH_PRESETS[PitchPreset("none")]

    try:
        noise_reduction_current = NOISE_REDUCTION_PRESETS[NoiseReductionPreset(user_settings.noise_reduction.preset)]
    except (ValueError, KeyError):
        noise_reduction_current = NOISE_REDUCTION_PRESETS[NoiseReductionPreset("none")]

    try:
        compressor_current = COMPRESSOR_PRESETS[CompressorPreset(user_settings.compressor.preset)]
    except (ValueError, KeyError):
        compressor_current = COMPRESSOR_PRESETS[CompressorPreset("none")]

    # Video effects
    try:
        brightness_current = BRIGHTNESS_PRESETS[BrightnessPreset(user_settings.brightness.preset)]
    except (ValueError, KeyError):
        brightness_current = BRIGHTNESS_PRESETS[BrightnessPreset("none")]

    try:
        contrast_current = CONTRAST_PRESETS[ContrastPreset(user_settings.contrast.preset)]
    except (ValueError, KeyError):
        contrast_current = CONTRAST_PRESETS[ContrastPreset("none")]

    try:
        saturation_current = SATURATION_PRESETS[SaturationPreset(user_settings.saturation.preset)]
    except (ValueError, KeyError):
        saturation_current = SATURATION_PRESETS[SaturationPreset("none")]

    try:
        blur_current = BLUR_PRESETS[BlurPreset(user_settings.blur.preset)]
    except (ValueError, KeyError):
        blur_current = BLUR_PRESETS[BlurPreset("none")]

    try:
        sharpen_current = SHARPEN_PRESETS[SharpenPreset(user_settings.sharpen.preset)]
    except (ValueError, KeyError):
        sharpen_current = SHARPEN_PRESETS[SharpenPreset("none")]

    try:
        transform_current = TRANSFORM_PRESETS[TransformPreset(user_settings.transform.preset)]
    except (ValueError, KeyError):
        transform_current = TRANSFORM_PRESETS[TransformPreset("none")]

    return {
        "user_settings": user_settings,
        # Audio presets
        "volume_presets": VOLUME_PRESETS_BY_STR,
        "tunnel_presets": TUNNEL_PRESETS_BY_STR,
        "frequency_presets": FREQUENCY_PRESETS_BY_STR,
        "speed_presets": SPEED_PRESETS_BY_STR,
        "pitch_presets": PITCH_PRESETS_BY_STR,
        "noise_reduction_presets": NOISE_REDUCTION_PRESETS_BY_STR,
        "compressor_presets": COMPRESSOR_PRESETS_BY_STR,
        # Video presets
        "brightness_presets": BRIGHTNESS_PRESETS_BY_STR,
        "contrast_presets": CONTRAST_PRESETS_BY_STR,
        "saturation_presets": SATURATION_PRESETS_BY_STR,
        "blur_presets": BLUR_PRESETS_BY_STR,
        "sharpen_presets": SHARPEN_PRESETS_BY_STR,
        "transform_presets": TRANSFORM_PRESETS_BY_STR,
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

    if tab == "video":
        return templates.TemplateResponse("partials/effects_video_accordion.html", context)
    else:
        return templates.TemplateResponse("partials/effects_audio_accordion.html", context)


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
