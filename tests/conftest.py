"""Shared pytest fixtures for audio filter tests."""

import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def sample_rate() -> int:
    """Standard sample rate for testing."""
    return 44100


@pytest.fixture
def presets_path() -> Path:
    """Path to presets.yml file."""
    return Path(__file__).parent.parent / "presets.yml"


# =============================================================================
# Audio Integration Test Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def test_audio_file(tmp_path_factory) -> Path:
    """Generate 10-second 440Hz sine wave test audio.

    Uses ffmpeg lavfi source to create deterministic synthetic audio.
    Session-scoped for efficiency across multiple tests.
    """
    tmp_dir = tmp_path_factory.mktemp("audio")
    output_path = tmp_dir / "test_sine_10s.wav"

    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=10:sample_rate=44100",
        "-y",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"ffmpeg not available or failed: {result.stderr}")

    return output_path


@pytest.fixture(scope="session")
def test_audio_with_noise(tmp_path_factory) -> Path:
    """Generate audio with added white noise for noise reduction tests.

    Creates a 10-second mix of 440Hz sine wave with white noise overlay.
    """
    tmp_dir = tmp_path_factory.mktemp("audio_noise")
    output_path = tmp_dir / "test_noisy_10s.wav"

    # Mix sine wave with white noise using amix filter
    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=10:sample_rate=44100",
        "-f", "lavfi",
        "-i", "anoisesrc=duration=10:sample_rate=44100:amplitude=0.1",
        "-filter_complex", "amix=inputs=2:duration=first",
        "-y",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"ffmpeg not available or failed: {result.stderr}")

    return output_path


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory) -> Path:
    """Temporary directory for test output files."""
    return tmp_path_factory.mktemp("output")


# =============================================================================
# Helper Utilities
# =============================================================================


def get_audio_duration(file_path: Path) -> float:
    """Use ffprobe to get audio duration in seconds.

    Args:
        file_path: Path to audio file

    Returns:
        Duration in seconds as float

    Raises:
        RuntimeError: If ffprobe fails or duration unavailable
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(file_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    duration_str = data.get("format", {}).get("duration")

    if duration_str is None:
        raise RuntimeError(f"Could not get duration from {file_path}")

    return float(duration_str)


def run_ffmpeg_filter(
    input_file: Path,
    output_file: Path,
    audio_filter: str,
) -> bool:
    """Execute ffmpeg with audio filter chain.

    Args:
        input_file: Path to input audio file
        output_file: Path for output audio file
        audio_filter: FFmpeg audio filter string (e.g., "atempo=2.0")

    Returns:
        True if successful, False otherwise
    """
    cmd = [
        "ffmpeg",
        "-i", str(input_file),
        "-af", audio_filter,
        "-y",
        str(output_file),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
