"""Shared pytest fixtures for audio filter tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_rate() -> int:
    """Standard sample rate for testing."""
    return 44100


@pytest.fixture
def presets_path() -> Path:
    """Path to presets.yml file."""
    return Path(__file__).parent.parent / "presets.yml"
