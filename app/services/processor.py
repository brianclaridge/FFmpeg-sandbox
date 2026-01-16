"""Audio/video processing service using FFmpeg."""

import re
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Generator

from loguru import logger

from app.config import OUTPUT_DIR
from app.services.filter_chain import build_audio_filter_chain


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

    # Build the audio filter chain using the centralized function
    audio_filter = build_audio_filter_chain(
        volume=volume,
        highpass=highpass,
        lowpass=lowpass,
        delays=delays,
        decays=decays,
    )

    # Check if volume is muted (0)
    is_muted = volume < 0.01

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
    elif audio_filter is None:
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


def process_video_with_filters(
    input_file: Path,
    start_time: str,
    end_time: str,
    audio_filter: str | None = None,
    video_filter: str | None = None,
    output_format: str = "mp4",
) -> Path:
    """
    Process video with both audio and video filter chains.

    Applies audio filters (-af) and video filters (-vf) simultaneously,
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
    elif output_format == "mkv":
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
        ])

    cmd.append(str(output_file))

    logger.info(f"Processing video with filters: {input_file.name}")
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


def process_audio_with_filters(
    input_file: Path,
    start_time: str,
    end_time: str,
    audio_filter: str | None = None,
    output_format: str = "mp3",
) -> Path:
    """
    Process audio with the full filter chain.

    Extracts audio from input file and applies all audio filters.
    This function should be used instead of process_audio() when
    the full filter chain (including speed, pitch, noise reduction,
    compressor) needs to be applied.

    Args:
        input_file: Path to source file (audio or video)
        start_time: Start timestamp (HH:MM:SS or HH:MM:SS.mmm)
        end_time: End timestamp (HH:MM:SS or HH:MM:SS.mmm)
        audio_filter: Complete audio filter chain string from build_audio_filter_chain()
        output_format: Output format (mp3, wav, flac)

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
        "-vn",  # No video output
    ]

    # Add audio filter chain if present
    if audio_filter:
        cmd.extend(["-af", audio_filter])

    # Output settings based on format
    if output_format == "mp3":
        cmd.extend(["-acodec", "libmp3lame", "-q:a", "4"])
    elif output_format == "wav":
        cmd.extend(["-acodec", "pcm_s16le"])
    elif output_format == "flac":
        cmd.extend(["-acodec", "flac"])

    cmd.append(str(output_file))

    logger.info(f"Processing audio with effects: {input_file.name}")
    logger.debug(f"Audio filter: {audio_filter}")
    logger.debug(f"Command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"ffmpeg error: {result.stderr}")
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    logger.info(f"Audio output saved: {output_file.name}")
    return output_file


def process_video_with_progress(
    input_file: Path,
    start_time: str,
    end_time: str,
    audio_filter: str | None = None,
    video_filter: str | None = None,
    output_format: str = "mp4",
    total_duration_ms: int = 0,
) -> Generator[dict, None, Path]:
    """
    Process video with progress updates via generator.

    Yields progress updates as dictionaries during processing.
    Returns the output file path when complete.

    Args:
        input_file: Path to source video file
        start_time: Start timestamp
        end_time: End timestamp
        audio_filter: Audio filter chain string
        video_filter: Video filter chain string
        output_format: Output format (mp4, mkv, webm)
        total_duration_ms: Total expected duration in milliseconds for progress calculation

    Yields:
        Progress dictionaries with keys: type, percent, current_ms, total_ms, log

    Returns:
        Path to the processed output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"processed_{timestamp}.{output_format}"

    cmd = [
        "ffmpeg",
        "-y",
        "-progress", "pipe:1",  # Progress to stdout
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
    elif output_format == "mkv":
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
        ])

    cmd.append(str(output_file))

    logger.info(f"Processing video with progress: {input_file.name}")
    logger.debug(f"Command: {' '.join(cmd)}")

    # Start process with Popen for real-time output
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    # Background thread to drain stderr and prevent buffer deadlock
    # Complex filter chains produce verbose warnings that fill the 64KB buffer
    stderr_lines = []

    def drain_stderr():
        for line in process.stderr:
            stderr_lines.append(line)

    stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
    stderr_thread.start()

    # Yield initial status
    yield {
        "type": "status",
        "message": "Starting FFmpeg processing...",
    }

    # Parse FFmpeg progress output
    current_time_ms = 0
    try:
        for line in process.stdout:
            line = line.strip()

            # Parse out_time_ms for progress
            if line.startswith("out_time_ms="):
                try:
                    current_time_ms = int(line.split("=")[1])
                    if total_duration_ms > 0:
                        percent = min(100, (current_time_ms / total_duration_ms) * 100)
                        yield {
                            "type": "progress",
                            "percent": round(percent, 1),
                            "current_ms": current_time_ms,
                            "total_ms": total_duration_ms,
                        }
                except (ValueError, IndexError):
                    pass

            # Capture frame info for log
            elif line.startswith("frame="):
                yield {
                    "type": "log",
                    "message": line,
                }

            # Check for completion
            elif line.startswith("progress=end"):
                yield {
                    "type": "progress",
                    "percent": 100,
                    "current_ms": total_duration_ms,
                    "total_ms": total_duration_ms,
                }

        # Wait for process to complete
        process.wait()
        stderr_thread.join(timeout=2.0)

        # Check for errors
        if process.returncode != 0:
            stderr = "".join(stderr_lines)
            logger.error(f"ffmpeg error: {stderr}")
            yield {
                "type": "error",
                "message": f"FFmpeg failed: {stderr[:500]}",
            }
            raise RuntimeError(f"ffmpeg failed: {stderr}")

        # Yield completion
        yield {
            "type": "complete",
            "output_file": output_file.name,
        }

        logger.info(f"Video output saved with progress: {output_file.name}")
        return output_file

    except Exception as e:
        process.kill()
        yield {
            "type": "error",
            "message": str(e),
        }
        raise
