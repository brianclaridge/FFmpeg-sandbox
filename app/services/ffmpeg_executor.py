"""FFmpeg subprocess execution wrapper."""

import subprocess
from pathlib import Path

from loguru import logger


class FFmpegError(Exception):
    """Exception raised when FFmpeg command fails."""

    def __init__(self, message: str, stderr: str = ""):
        self.message = message
        self.stderr = stderr
        super().__init__(self.message)


def run_ffmpeg_command(
    cmd: list[str],
    description: str = "FFmpeg operation",
    timeout: int | None = None,
) -> subprocess.CompletedProcess:
    """
    Execute an FFmpeg command with logging and error handling.

    Args:
        cmd: Complete FFmpeg command as list of strings
        description: Human-readable description for logging
        timeout: Optional timeout in seconds

    Returns:
        CompletedProcess result

    Raises:
        FFmpegError: If the command fails
    """
    logger.debug(f"{description}: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise FFmpegError(f"{description} failed", stderr=result.stderr)

        return result

    except subprocess.TimeoutExpired as e:
        logger.error(f"FFmpeg timeout: {description}")
        raise FFmpegError(f"{description} timed out after {timeout}s") from e


def run_ffprobe_command(
    cmd: list[str],
    description: str = "FFprobe operation",
    timeout: int = 10,
) -> subprocess.CompletedProcess:
    """
    Execute an FFprobe command with logging and error handling.

    Args:
        cmd: Complete FFprobe command as list of strings
        description: Human-readable description for logging
        timeout: Timeout in seconds (default 10)

    Returns:
        CompletedProcess result

    Raises:
        FFmpegError: If the command fails
    """
    logger.debug(f"{description}: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            logger.warning(f"FFprobe error: {result.stderr}")
            raise FFmpegError(f"{description} failed", stderr=result.stderr)

        return result

    except subprocess.TimeoutExpired as e:
        logger.warning(f"FFprobe timeout: {description}")
        raise FFmpegError(f"{description} timed out after {timeout}s") from e
