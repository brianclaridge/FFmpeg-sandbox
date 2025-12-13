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
