"""Tests for audio filter builders."""

import pytest

from app.services.filters_audio import (
    build_speed_filter,
    build_pitch_filter,
    build_noise_reduction_filter,
    build_compressor_filter,
)


class TestBuildSpeedFilter:
    """Tests for build_speed_filter function."""

    def test_speed_1x_returns_empty(self):
        """Test that 1.0 speed returns empty string (no filter)."""
        result = build_speed_filter(1.0)
        assert result == ""

    def test_speed_within_atempo_range(self):
        """Test speeds within 0.5-2.0 use single atempo."""
        result = build_speed_filter(1.5)
        assert result == "atempo=1.5"

    def test_speed_at_lower_boundary(self):
        """Test speed at atempo lower boundary."""
        result = build_speed_filter(0.5)
        assert result == "atempo=0.5"

    def test_speed_at_upper_boundary(self):
        """Test speed at atempo upper boundary."""
        result = build_speed_filter(2.0)
        assert result == "atempo=2.0"

    def test_speed_4x_chains_filters(self):
        """Test 4x speed chains multiple atempo filters."""
        result = build_speed_filter(4.0)
        # 4.0 = 2.0 * 2.0, should chain two atempo=2.0
        assert "atempo=2.0" in result
        assert result.count("atempo") == 2

    def test_speed_0_25x_chains_filters(self):
        """Test 0.25x speed chains multiple atempo filters."""
        result = build_speed_filter(0.25)
        # 0.25 = 0.5 * 0.5, should chain two atempo=0.5
        assert "atempo=0.5" in result
        assert result.count("atempo") == 2

    def test_speed_3x_chains_correctly(self):
        """Test 3x speed uses atempo=2.0 + additional atempo."""
        result = build_speed_filter(3.0)
        # 3.0 = 2.0 * 1.5
        assert "atempo=2.0" in result
        assert result.count("atempo") == 2

    @pytest.mark.parametrize("speed,expected_count", [
        (0.25, 2),  # 0.5 * 0.5
        (0.5, 1),
        (1.0, 0),   # No filter
        (2.0, 1),
        (4.0, 2),   # 2.0 * 2.0
    ])
    def test_speed_filter_count(self, speed, expected_count):
        """Parametrized test for atempo filter count."""
        result = build_speed_filter(speed)
        actual_count = result.count("atempo") if result else 0
        assert actual_count == expected_count


class TestBuildPitchFilter:
    """Tests for build_pitch_filter function."""

    def test_pitch_zero_returns_empty(self):
        """Test 0 semitones returns empty string."""
        result = build_pitch_filter(0.0)
        assert result == ""

    def test_pitch_positive_semitones(self):
        """Test positive pitch shift."""
        result = build_pitch_filter(4.0)
        assert "asetrate=" in result
        assert "atempo=" in result
        assert "aresample=44100" in result

    def test_pitch_negative_semitones(self):
        """Test negative pitch shift."""
        result = build_pitch_filter(-4.0)
        assert "asetrate=" in result
        assert "atempo=" in result
        assert "aresample=44100" in result

    def test_pitch_octave_up_sample_rate(self):
        """Test +12 semitones doubles sample rate."""
        result = build_pitch_filter(12.0, sample_rate=44100)
        # ratio = 2^(12/12) = 2.0
        # new_rate = 44100 * 2 = 88200
        assert "asetrate=88200" in result

    def test_pitch_octave_down_sample_rate(self):
        """Test -12 semitones halves sample rate."""
        result = build_pitch_filter(-12.0, sample_rate=44100)
        # ratio = 2^(-12/12) = 0.5
        # new_rate = 44100 * 0.5 = 22050
        assert "asetrate=22050" in result

    def test_pitch_custom_sample_rate(self):
        """Test pitch with non-default sample rate."""
        result = build_pitch_filter(0.0, sample_rate=48000)
        assert result == ""  # No change, so empty

        result = build_pitch_filter(12.0, sample_rate=48000)
        assert "aresample=48000" in result

    def test_pitch_tempo_compensation_octave_up(self):
        """Test that atempo compensates for pitch change (octave up)."""
        result = build_pitch_filter(12.0)
        # For +12 semitones, tempo_compensation = 1/2 = 0.5
        assert "atempo=0.5" in result

    def test_pitch_tempo_compensation_octave_down(self):
        """Test that atempo compensates for pitch change (octave down)."""
        result = build_pitch_filter(-12.0)
        # For -12 semitones, tempo_compensation = 1/0.5 = 2.0
        assert "atempo=2.0" in result

    @pytest.mark.parametrize("semitones", [-12, -8, -4, 0, 4, 8, 12])
    def test_pitch_preset_values(self, semitones):
        """Test pitch values matching presets.yml."""
        result = build_pitch_filter(float(semitones))
        if semitones == 0:
            assert result == ""
        else:
            assert "asetrate=" in result


class TestBuildNoiseReductionFilter:
    """Tests for build_noise_reduction_filter function."""

    def test_noise_reduction_zero_returns_empty(self):
        """Test 0.0 reduction returns empty string."""
        result = build_noise_reduction_filter(-30.0, 0.0)
        assert result == ""

    def test_noise_reduction_active(self):
        """Test active noise reduction."""
        result = build_noise_reduction_filter(-40.0, 0.5)
        assert result == "afftdn=nf=-40.0:nr=50.0"

    def test_noise_reduction_maximum(self):
        """Test maximum noise reduction."""
        result = build_noise_reduction_filter(-50.0, 1.0)
        assert "afftdn=nf=-50.0:nr=100" in result

    def test_noise_floor_values(self):
        """Test various noise floor values."""
        result = build_noise_reduction_filter(-30.0, 0.5)
        assert "nf=-30.0" in result

        result = build_noise_reduction_filter(-80.0, 0.5)
        assert "nf=-80.0" in result

    @pytest.mark.parametrize("reduction,expected_nr", [
        (0.0, None),  # Returns empty
        (0.5, "50"),
        (0.7, "70"),
        (0.9, "90"),
        (1.0, "100"),
    ])
    def test_noise_reduction_scaling(self, reduction, expected_nr):
        """Test that 0-1 reduction maps to 0-100 for FFmpeg."""
        result = build_noise_reduction_filter(-40.0, reduction)
        if expected_nr is None:
            assert result == ""
        else:
            assert f"nr={expected_nr}" in result


class TestBuildCompressorFilter:
    """Tests for build_compressor_filter function."""

    def test_compressor_ratio_1_returns_empty(self):
        """Test ratio 1.0 (no compression) returns empty."""
        result = build_compressor_filter(-20.0, 1.0, 20.0, 250.0, 0.0)
        assert result == ""

    def test_compressor_ratio_below_1_returns_empty(self):
        """Test ratio below 1.0 returns empty."""
        result = build_compressor_filter(-20.0, 0.5, 20.0, 250.0, 0.0)
        assert result == ""

    def test_compressor_active(self):
        """Test active compressor filter."""
        result = build_compressor_filter(-20.0, 4.0, 10.0, 150.0, 4.0)
        assert "acompressor=" in result
        assert "threshold=-20.0dB" in result
        assert "ratio=4.0" in result
        assert "attack=10.0" in result
        assert "release=150.0" in result
        assert "makeup=4.0dB" in result
