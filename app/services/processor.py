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
        volume: Volume multiplier (0.5-4.0)
        highpass: High-pass filter frequency in Hz
        lowpass: Low-pass filter frequency in Hz
        delays: Pipe-separated delay values in ms
        decays: Pipe-separated decay values (0-1)

    Returns:
        Path to the processed output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"processed_{timestamp}.mp3"

    audio_filter = (
        f"volume={volume},"
        f"highpass=f={highpass},"
        f"lowpass=f={lowpass},"
        f"aecho=0.8:0.85:{delays}:{decays}"
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
