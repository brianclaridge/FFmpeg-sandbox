"""Tests for preset loading and validation."""

import pytest
from pathlib import Path

from app.services.presets import load_presets, get_speed_presets, get_pitch_presets, get_noise_reduction_presets
from app.models import SpeedConfig, PitchConfig, NoiseReductionConfig


class TestLoadPresets:
    """Tests for load_presets function."""

    def test_load_presets_success(self, presets_path):
        """Test loading presets from file."""
        if presets_path.exists():
            presets = load_presets(presets_path)
            assert "audio" in presets
            assert "video" in presets

    def test_presets_file_exists(self, presets_path):
        """Test that presets.yml file exists."""
        assert presets_path.exists(), f"presets.yml not found at {presets_path}"


class TestSpeedPresetsValidation:
    """Tests for speed preset values against constraints."""

    def test_speed_presets_within_constraints(self, presets_path):
        """Test all speed presets are within 0.25-4.0 range."""
        if presets_path.exists():
            load_presets(presets_path)
            speed_presets = get_speed_presets()
            for key, preset in speed_presets.items():
                assert 0.25 <= preset.speed <= 4.0, f"Speed preset '{key}' value {preset.speed} out of range"

    def test_speed_presets_not_empty(self, presets_path):
        """Test that speed presets exist."""
        if presets_path.exists():
            load_presets(presets_path)
            speed_presets = get_speed_presets()
            assert len(speed_presets) > 0, "No speed presets found"


class TestPitchPresetsValidation:
    """Tests for pitch preset values against constraints."""

    def test_pitch_presets_within_constraints(self, presets_path):
        """Test all pitch presets are within -12 to +12 semitones."""
        if presets_path.exists():
            load_presets(presets_path)
            pitch_presets = get_pitch_presets()
            for key, preset in pitch_presets.items():
                assert -12.0 <= preset.semitones <= 12.0, f"Pitch preset '{key}' value {preset.semitones} out of range"

    def test_pitch_presets_not_empty(self, presets_path):
        """Test that pitch presets exist."""
        if presets_path.exists():
            load_presets(presets_path)
            pitch_presets = get_pitch_presets()
            assert len(pitch_presets) > 0, "No pitch presets found"


class TestNoiseReductionPresetsValidation:
    """Tests for noise reduction preset values against constraints."""

    def test_noise_reduction_presets_within_constraints(self, presets_path):
        """Test all noise reduction presets are within valid ranges."""
        if presets_path.exists():
            load_presets(presets_path)
            nr_presets = get_noise_reduction_presets()
            for key, preset in nr_presets.items():
                assert -80.0 <= preset.noise_floor <= -20.0, f"Noise preset '{key}' floor {preset.noise_floor} out of range"
                assert 0.0 <= preset.noise_reduction <= 1.0, f"Noise preset '{key}' reduction {preset.noise_reduction} out of range"

    def test_noise_reduction_presets_not_empty(self, presets_path):
        """Test that noise reduction presets exist."""
        if presets_path.exists():
            load_presets(presets_path)
            nr_presets = get_noise_reduction_presets()
            assert len(nr_presets) > 0, "No noise reduction presets found"


class TestPresetExtremeValues:
    """Tests for extreme preset values against new constraints."""

    def test_speed_config_allows_4x(self):
        """Test that 4x speed preset would be valid."""
        config = SpeedConfig(name="4x", description="4x speed", speed=4.0)
        assert config.speed == 4.0

    def test_speed_config_allows_quarter(self):
        """Test that 0.25x speed preset would be valid."""
        config = SpeedConfig(name="0.25x", description="Quarter speed", speed=0.25)
        assert config.speed == 0.25

    def test_pitch_config_allows_chipmunk(self):
        """Test that chipmunk preset (+8 semitones) is valid."""
        config = PitchConfig(name="Chipmunk", description="High", semitones=8.0)
        assert config.semitones == 8.0

    def test_pitch_config_allows_octave_shift(self):
        """Test that full octave shift is valid."""
        config_up = PitchConfig(name="Octave Up", description="Up", semitones=12.0)
        config_down = PitchConfig(name="Octave Down", description="Down", semitones=-12.0)
        assert config_up.semitones == 12.0
        assert config_down.semitones == -12.0

    def test_noise_reduction_config_allows_extreme_floor(self):
        """Test that extreme noise floor values are valid."""
        config = NoiseReductionConfig(
            name="Extreme", description="Deep floor",
            noise_floor=-80.0, noise_reduction=0.9
        )
        assert config.noise_floor == -80.0
