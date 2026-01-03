"""Tests for Pydantic model constraints."""

import pytest
from pydantic import ValidationError

from app.models import SpeedConfig, PitchConfig, NoiseReductionConfig


class TestSpeedConfig:
    """Tests for SpeedConfig validation."""

    def test_valid_speed_normal(self):
        """Test normal speed value."""
        config = SpeedConfig(name="Normal", description="Normal speed", speed=1.0)
        assert config.speed == 1.0

    def test_valid_speed_minimum(self):
        """Test minimum allowed speed."""
        config = SpeedConfig(name="Min", description="Minimum", speed=0.25)
        assert config.speed == 0.25

    def test_valid_speed_maximum(self):
        """Test maximum allowed speed (4x)."""
        config = SpeedConfig(name="Max", description="Maximum", speed=4.0)
        assert config.speed == 4.0

    def test_valid_speed_preset_values(self):
        """Test all preset speed values are valid."""
        preset_speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        for speed in preset_speeds:
            config = SpeedConfig(name="Test", description="Test", speed=speed)
            assert config.speed == speed

    def test_invalid_speed_below_minimum(self):
        """Test speed below minimum raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SpeedConfig(name="Too Slow", description="Invalid", speed=0.1)
        assert "greater than or equal to 0.25" in str(exc_info.value)

    def test_invalid_speed_above_maximum(self):
        """Test speed above maximum raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SpeedConfig(name="Too Fast", description="Invalid", speed=5.0)
        assert "less than or equal to 4" in str(exc_info.value)

    def test_invalid_speed_zero(self):
        """Test zero speed raises ValidationError."""
        with pytest.raises(ValidationError):
            SpeedConfig(name="Zero", description="Invalid", speed=0.0)

    def test_invalid_speed_negative(self):
        """Test negative speed raises ValidationError."""
        with pytest.raises(ValidationError):
            SpeedConfig(name="Negative", description="Invalid", speed=-1.0)


class TestPitchConfig:
    """Tests for PitchConfig validation."""

    def test_valid_pitch_normal(self):
        """Test normal pitch (no change)."""
        config = PitchConfig(name="Normal", description="No change", semitones=0.0)
        assert config.semitones == 0.0

    def test_valid_pitch_octave_up(self):
        """Test one octave up (+12 semitones)."""
        config = PitchConfig(name="Octave Up", description="High", semitones=12.0)
        assert config.semitones == 12.0

    def test_valid_pitch_octave_down(self):
        """Test one octave down (-12 semitones)."""
        config = PitchConfig(name="Octave Down", description="Low", semitones=-12.0)
        assert config.semitones == -12.0

    def test_valid_pitch_fractional(self):
        """Test fractional semitone values."""
        config = PitchConfig(name="Slight", description="Slight shift", semitones=0.5)
        assert config.semitones == 0.5

    def test_valid_pitch_preset_values(self):
        """Test all preset pitch values are valid."""
        preset_semitones = [-4.0, 0.0, 4.0, 8.0]
        for semitones in preset_semitones:
            config = PitchConfig(name="Test", description="Test", semitones=semitones)
            assert config.semitones == semitones

    def test_invalid_pitch_above_maximum(self):
        """Test pitch above +12 semitones raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PitchConfig(name="Too High", description="Invalid", semitones=13.0)
        assert "less than or equal to 12" in str(exc_info.value)

    def test_invalid_pitch_below_minimum(self):
        """Test pitch below -12 semitones raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PitchConfig(name="Too Low", description="Invalid", semitones=-13.0)
        assert "greater than or equal to -12" in str(exc_info.value)


class TestNoiseReductionConfig:
    """Tests for NoiseReductionConfig validation."""

    def test_valid_noise_reduction_off(self):
        """Test noise reduction off."""
        config = NoiseReductionConfig(
            name="Off", description="Disabled",
            noise_floor=-25.0, noise_reduction=0.0
        )
        assert config.noise_reduction == 0.0

    def test_valid_noise_reduction_maximum(self):
        """Test maximum noise reduction."""
        config = NoiseReductionConfig(
            name="Max", description="Maximum",
            noise_floor=-50.0, noise_reduction=1.0
        )
        assert config.noise_reduction == 1.0

    def test_valid_noise_floor_high_boundary(self):
        """Test noise floor at high boundary (-20 dB)."""
        config = NoiseReductionConfig(
            name="High", description="High floor",
            noise_floor=-20.0, noise_reduction=0.5
        )
        assert config.noise_floor == -20.0

    def test_valid_noise_floor_low_boundary(self):
        """Test noise floor at low boundary (-80 dB)."""
        config = NoiseReductionConfig(
            name="Low", description="Low floor",
            noise_floor=-80.0, noise_reduction=0.5
        )
        assert config.noise_floor == -80.0

    def test_valid_preset_values(self):
        """Test all preset noise reduction values are valid."""
        presets = [
            (-30.0, 0.5),  # light
            (-40.0, 0.7),  # medium
            (-50.0, 0.9),  # heavy
        ]
        for noise_floor, noise_reduction in presets:
            config = NoiseReductionConfig(
                name="Test", description="Test",
                noise_floor=noise_floor, noise_reduction=noise_reduction
            )
            assert config.noise_floor == noise_floor
            assert config.noise_reduction == noise_reduction

    def test_invalid_noise_floor_too_high(self):
        """Test noise floor above -20 dB raises ValidationError."""
        with pytest.raises(ValidationError):
            NoiseReductionConfig(
                name="Invalid", description="Bad floor",
                noise_floor=-10.0, noise_reduction=0.5
            )

    def test_invalid_noise_floor_too_low(self):
        """Test noise floor below -80 dB raises ValidationError."""
        with pytest.raises(ValidationError):
            NoiseReductionConfig(
                name="Invalid", description="Bad floor",
                noise_floor=-90.0, noise_reduction=0.5
            )

    def test_invalid_noise_reduction_negative(self):
        """Test negative noise reduction raises ValidationError."""
        with pytest.raises(ValidationError):
            NoiseReductionConfig(
                name="Invalid", description="Bad reduction",
                noise_floor=-40.0, noise_reduction=-0.1
            )

    def test_invalid_noise_reduction_above_one(self):
        """Test noise reduction above 1.0 raises ValidationError."""
        with pytest.raises(ValidationError):
            NoiseReductionConfig(
                name="Invalid", description="Bad reduction",
                noise_floor=-40.0, noise_reduction=1.5
            )
