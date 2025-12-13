"""Audio processing service using ffmpeg."""

import subprocess
from pathlib import Path
from datetime import datetime

from loguru import logger

from app.config import OUTPUT_DIR


def process_audio(
    input_file: Path,
    start_time: str,
    end_time: str,
    volume: float,
    highpass: int,
    lowpass: int,
    delays: str,
    decays: str,
) -> Path:
    """
    Process audio from video file with tunnel effects.

    Args:
        input_file: Path to source video/audio file
        start_time: Start timestamp (HH:MM:SS or HH:MM:SS.mmm)
        end_time: End timestamp (HH:MM:SS or HH:MM:SS.mmm)
        volume: Volume multiplier (0.0-4.0, 0=muted, 1=original)
        highpass: High-pass filter frequency in Hz
        lowpass: Low-pass filter frequency in Hz
        delays: Pipe-separated delay values in ms
        decays: Pipe-separated decay values (0-1)

    Returns:
        Path to the processed output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"processed_{timestamp}.mp3"

    # Check if all decay values are 0 (no echo effect)
    decay_values = [float(d) for d in decays.split("|") if d.strip()]
    has_echo = any(d > 0 for d in decay_values)

    # Check if volume is muted (0)
    is_muted = volume < 0.01

    # Check if all settings are neutral (no processing needed)
    is_neutral = (
        abs(volume - 1.0) < 0.01 and
        highpass <= 20 and
        lowpass >= 20000 and
        not has_echo
    )

    if is_muted:
        # Produce silent audio without filter processing
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-ss", start_time,
            "-to", end_time,
            "-vn",
            "-af", "volume=0",
            "-acodec", "libmp3lame",
            "-q:a", "4",
            str(output_file),
        ]
    elif is_neutral:
        # Pure extraction - no audio filters applied
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-ss", start_time,
            "-to", end_time,
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "4",
            str(output_file),
        ]
    else:
        if has_echo:
            audio_filter = (
                f"volume={volume},"
                f"highpass=f={highpass},"
                f"lowpass=f={lowpass},"
                f"aecho=0.8:0.85:{delays}:{decays}"
            )
        else:
            audio_filter = (
                f"volume={volume},"
                f"highpass=f={highpass},"
                f"lowpass=f={lowpass}"
            )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-ss", start_time,
            "-to", end_time,
            "-af", audio_filter,
            "-vn",
            str(output_file),
        ]

    logger.info(f"Processing audio: {input_file.name}")
    logger.debug(f"Command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"ffmpeg error: {result.stderr}")
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    logger.info(f"Output saved: {output_file.name}")
    return output_file


def get_file_duration(file_path: Path) -> int | None:
    """
    Get duration of audio/video file in milliseconds using ffprobe.

    Args:
        file_path: Path to the media file

    Returns:
        Duration in milliseconds, or None if detection fails.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            duration_seconds = float(result.stdout.strip())
            return int(duration_seconds * 1000)
    except (subprocess.TimeoutExpired, ValueError) as e:
        logger.warning(f"Failed to get duration for {file_path}: {e}")

    return None


def format_duration_ms(ms: int) -> str:
    """Format milliseconds as HH:MM:SS.mmm"""
    total_seconds = ms // 1000
    milliseconds = ms % 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def get_input_files(input_dir: Path) -> list[Path]:
    """Get list of video/audio files in input directory."""
    extensions = {".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".flac"}
    files = []
    for ext in extensions:
        files.extend(input_dir.glob(f"*{ext}"))
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def get_file_metadata(file_path: Path) -> dict:
    """
    Get detailed metadata for audio/video file using ffprobe.

    Returns dict with: file_type, size_bytes, size_formatted, duration_ms,
    duration_formatted, codec_name, sample_rate, channels, bit_rate,
    and for video: width, height, frame_rate.
    """
    import json

    metadata = {
        "filename": file_path.name,
        "file_type": "unknown",
        "size_bytes": 0,
        "size_formatted": "0 B",
    }

    # Get file size
    if file_path.exists():
        size = file_path.stat().st_size
        metadata["size_bytes"] = size
        metadata["size_formatted"] = format_file_size(size)

    # Determine file type from extension
    ext = file_path.suffix.lower()
    video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
    audio_exts = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

    if ext in video_exts:
        metadata["file_type"] = "video"
    elif ext in audio_exts:
        metadata["file_type"] = "audio"

    # Get detailed info from ffprobe
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            probe_data = json.loads(result.stdout)

            # Format info
            fmt = probe_data.get("format", {})
            if "duration" in fmt:
                duration_ms = int(float(fmt["duration"]) * 1000)
                metadata["duration_ms"] = duration_ms
                metadata["duration_formatted"] = format_duration_ms(duration_ms)
            if "bit_rate" in fmt:
                metadata["bit_rate"] = int(fmt["bit_rate"])
                metadata["bit_rate_formatted"] = format_bitrate(int(fmt["bit_rate"]))

            # Stream info
            streams = probe_data.get("streams", [])
            for stream in streams:
                codec_type = stream.get("codec_type")

                if codec_type == "video" and "width" not in metadata:
                    metadata["video_codec"] = stream.get("codec_name", "unknown")
                    metadata["width"] = stream.get("width")
                    metadata["height"] = stream.get("height")
                    # Calculate frame rate from r_frame_rate (e.g., "30/1")
                    r_frame_rate = stream.get("r_frame_rate", "0/1")
                    if "/" in r_frame_rate:
                        num, den = r_frame_rate.split("/")
                        if int(den) > 0:
                            metadata["frame_rate"] = round(int(num) / int(den), 2)

                elif codec_type == "audio" and "audio_codec" not in metadata:
                    metadata["audio_codec"] = stream.get("codec_name", "unknown")
                    metadata["sample_rate"] = stream.get("sample_rate")
                    metadata["channels"] = stream.get("channels")

    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to get metadata for {file_path}: {e}")

    return metadata


def format_file_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_bitrate(bitrate: int) -> str:
    """Format bitrate as human-readable string."""
    if bitrate >= 1_000_000:
        return f"{bitrate / 1_000_000:.1f} Mbps"
    elif bitrate >= 1000:
        return f"{bitrate / 1000:.0f} kbps"
    return f"{bitrate} bps"


# ============ AUDIO FILTER BUILDERS ============

def build_speed_filter(speed: float) -> str:
    """
    Build atempo filter for speed adjustment.

    FFmpeg atempo only supports 0.5-2.0 range, so we chain multiple
    filters for values outside this range.
    """
    if speed == 1.0:
        return ""

    filters = []
    remaining = speed

    # Chain atempo filters to achieve desired speed
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5

    # Add final atempo for remaining adjustment
    if 0.5 <= remaining <= 2.0 and remaining != 1.0:
        filters.append(f"atempo={remaining}")

    return ",".join(filters)


def build_pitch_filter(semitones: float, sample_rate: int = 44100) -> str:
    """
    Build pitch shift filter using asetrate + atempo.

    This shifts pitch without changing playback speed by:
    1. Changing sample rate to shift pitch
    2. Using atempo to compensate for speed change
    """
    if semitones == 0.0:
        return ""

    # Calculate the pitch ratio (2^(semitones/12))
    import math
    ratio = math.pow(2, semitones / 12)

    # asetrate changes pitch, atempo compensates speed
    new_rate = int(sample_rate * ratio)
    tempo_compensation = 1 / ratio

    return f"asetrate={new_rate},atempo={tempo_compensation:.6f},aresample={sample_rate}"


def build_noise_reduction_filter(noise_floor: float, noise_reduction: float) -> str:
    """
    Build afftdn (FFT-based denoiser) filter.

    Args:
        noise_floor: Noise floor in dB (-20 to -80)
        noise_reduction: Reduction amount (0.0 to 1.0)
    """
    if noise_reduction == 0.0:
        return ""

    return f"afftdn=nf={noise_floor}:nr={noise_reduction * 100}"


def build_compressor_filter(
    threshold: float,
    ratio: float,
    attack: float,
    release: float,
    makeup: float,
) -> str:
    """
    Build acompressor filter for dynamic range compression.

    Args:
        threshold: dB level where compression starts
        ratio: Compression ratio (e.g., 4 = 4:1)
        attack: Attack time in ms
        release: Release time in ms
        makeup: Makeup gain in dB
    """
    if ratio <= 1.0:
        return ""

    return (
        f"acompressor=threshold={threshold}dB:ratio={ratio}:"
        f"attack={attack}:release={release}:makeup={makeup}dB"
    )


# ============ VIDEO FILTER BUILDERS ============

def build_eq_filter(brightness: float, contrast: float, saturation: float) -> str:
    """
    Build eq filter for brightness/contrast/saturation adjustment.

    All values have "no effect" defaults: brightness=0, contrast=1, saturation=1
    """
    # Check if any adjustments needed
    if brightness == 0.0 and contrast == 1.0 and saturation == 1.0:
        return ""

    return f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"


def build_blur_filter(sigma: float) -> str:
    """Build gblur (Gaussian blur) filter."""
    if sigma <= 0:
        return ""

    return f"gblur=sigma={sigma}"


def build_sharpen_filter(amount: float) -> str:
    """
    Build unsharp filter for sharpening.

    Uses 5x5 luma matrix with specified amount.
    """
    if amount <= 0:
        return ""

    return f"unsharp=5:5:{amount}:5:5:0"


def build_transform_filter(filter_str: str) -> str:
    """Return transform filter string directly (hflip, vflip, transpose, etc.)."""
    return filter_str if filter_str else ""


# ============ FILTER CHAIN BUILDERS ============

def build_audio_filter_chain(
    volume: float = 1.0,
    highpass: int = 20,
    lowpass: int = 20000,
    delays: str = "",
    decays: str = "",
    speed: float = 1.0,
    pitch_semitones: float = 0.0,
    noise_floor: float = -25.0,
    noise_reduction: float = 0.0,
    comp_threshold: float = 0.0,
    comp_ratio: float = 1.0,
    comp_attack: float = 20.0,
    comp_release: float = 250.0,
    comp_makeup: float = 0.0,
) -> str | None:
    """
    Build complete audio filter chain from all audio effect settings.

    Returns None if no effects are active.
    """
    filters = []

    # Volume
    if volume != 1.0:
        filters.append(f"volume={volume}")

    # Frequency (highpass/lowpass)
    if highpass > 20:
        filters.append(f"highpass=f={highpass}")
    if lowpass < 20000:
        filters.append(f"lowpass=f={lowpass}")

    # Tunnel/echo
    if delays and decays:
        decay_values = [float(d) for d in decays.split("|") if d.strip()]
        if any(d > 0 for d in decay_values):
            filters.append(f"aecho=0.8:0.85:{delays}:{decays}")

    # Speed
    speed_filter = build_speed_filter(speed)
    if speed_filter:
        filters.append(speed_filter)

    # Pitch
    pitch_filter = build_pitch_filter(pitch_semitones)
    if pitch_filter:
        filters.append(pitch_filter)

    # Noise reduction
    nr_filter = build_noise_reduction_filter(noise_floor, noise_reduction)
    if nr_filter:
        filters.append(nr_filter)

    # Compressor
    comp_filter = build_compressor_filter(
        comp_threshold, comp_ratio, comp_attack, comp_release, comp_makeup
    )
    if comp_filter:
        filters.append(comp_filter)

    return ",".join(filters) if filters else None


def build_video_filter_chain(
    brightness: float = 0.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    blur_sigma: float = 0.0,
    sharpen_amount: float = 0.0,
    transform: str = "",
    speed: float = 1.0,
) -> str | None:
    """
    Build complete video filter chain from all video effect settings.

    Returns None if no effects are active.
    """
    filters = []

    # EQ (brightness/contrast/saturation)
    eq_filter = build_eq_filter(brightness, contrast, saturation)
    if eq_filter:
        filters.append(eq_filter)

    # Blur
    blur_filter = build_blur_filter(blur_sigma)
    if blur_filter:
        filters.append(blur_filter)

    # Sharpen
    sharpen_filter = build_sharpen_filter(sharpen_amount)
    if sharpen_filter:
        filters.append(sharpen_filter)

    # Transform
    transform_filter = build_transform_filter(transform)
    if transform_filter:
        filters.append(transform_filter)

    # Speed (video uses setpts)
    if speed != 1.0:
        pts_factor = 1 / speed
        filters.append(f"setpts={pts_factor}*PTS")

    return ",".join(filters) if filters else None


def process_video_with_effects(
    input_file: Path,
    start_time: str,
    end_time: str,
    audio_filter: str | None = None,
    video_filter: str | None = None,
    output_format: str = "mp4",
) -> Path:
    """
    Process video with both audio and video filter chains.

    Applies audio effects (-af) and video effects (-vf) simultaneously,
    ensuring A/V synchronization when speed changes are involved.

    Args:
        input_file: Path to source video file
        start_time: Start timestamp (HH:MM:SS or HH:MM:SS.mmm)
        end_time: End timestamp (HH:MM:SS or HH:MM:SS.mmm)
        audio_filter: Complete audio filter chain string or None
        video_filter: Complete video filter chain string or None
        output_format: Output format (mp4, mkv, webm)

    Returns:
        Path to the processed output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"processed_{timestamp}.{output_format}"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_file),
        "-ss", start_time,
        "-to", end_time,
    ]

    # Add audio filter chain if present
    if audio_filter:
        cmd.extend(["-af", audio_filter])

    # Add video filter chain if present
    if video_filter:
        cmd.extend(["-vf", video_filter])

    # Output settings based on format
    if output_format == "mp4":
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
        ])
    elif output_format == "webm":
        cmd.extend([
            "-c:v", "libvpx-vp9",
            "-crf", "30",
            "-b:v", "0",
            "-c:a", "libopus",
            "-b:a", "128k",
        ])

    cmd.append(str(output_file))

    logger.info(f"Processing video with effects: {input_file.name}")
    logger.debug(f"Audio filter: {audio_filter}")
    logger.debug(f"Video filter: {video_filter}")
    logger.debug(f"Command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"ffmpeg error: {result.stderr}")
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    logger.info(f"Video output saved: {output_file.name}")
    return output_file
